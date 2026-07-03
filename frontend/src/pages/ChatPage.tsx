import { useEffect, useRef, useState, useCallback } from "react";
import { useAuth } from "../hooks/useAuth";
import { useWebSocket } from "../hooks/useWebSocket";
import api from "../services/api";

// ── Types ──────────────────────────────────────────────────────────────────

interface Member { user_id: string; username: string; display_name: string | null; online: boolean; }
interface Chat { id: string; is_group: boolean; name: string | null; members: Member[]; }
interface Message {
  id: string; chat_id: string; content: string | null; message_type: string;
  deleted_for_everyone: boolean; created_at: string;
  sender: { id: string; username: string; display_name: string | null } | null;
  replied_to_id: string | null;
}
interface UserPublic { id: string; username: string; display_name: string | null; online: boolean; }

// ── Helpers ────────────────────────────────────────────────────────────────

function fmt(iso: string) {
  const d = new Date(iso);
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function initials(name: string | null | undefined) {
  return (name ?? "?").slice(0, 2).toUpperCase();
}

// ── Avatar ─────────────────────────────────────────────────────────────────

function Avatar({ name, online, size = "md" }: { name?: string | null; online?: boolean; size?: "sm" | "md" | "lg" }) {
  const sz = { sm: "w-8 h-8 text-xs", md: "w-10 h-10 text-sm", lg: "w-12 h-12 text-base" }[size];
  const dot = { sm: "w-2 h-2", md: "w-2.5 h-2.5", lg: "w-3 h-3" }[size];
  return (
    <div className="relative flex-shrink-0">
      <div className={`${sz} rounded-full bg-sky-700 flex items-center justify-center font-bold text-white`}>
        {initials(name)}
      </div>
      {online !== undefined && (
        <span className={`absolute bottom-0 right-0 ${dot} rounded-full border-2 border-slate-900 ${online ? "bg-emerald-400" : "bg-slate-600"}`} />
      )}
    </div>
  );
}

// ── Main Page ──────────────────────────────────────────────────────────────

export default function ChatPage() {
  const { user, logout } = useAuth();
  const { connected, send, subscribe } = useWebSocket();

  const [chats, setChats] = useState<Chat[]>([]);
  const [activeChat, setActiveChat] = useState<Chat | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [hasMore, setHasMore] = useState(false);
  const [text, setText] = useState("");
  const [searchQ, setSearchQ] = useState("");
  const [searchResults, setSearchResults] = useState<UserPublic[]>([]);
  const [typing, setTyping] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const typingTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Load chats
  useEffect(() => {
    api.get("/chats").then(r => setChats(r.data));
  }, []);

  // Load messages when chat changes
  useEffect(() => {
    if (!activeChat) return;
    setLoading(true);
    setMessages([]);
    api.get(`/chats/${activeChat.id}/messages`, { params: { limit: 50 } })
      .then(r => { setMessages(r.data.items); setHasMore(r.data.has_more); })
      .finally(() => setLoading(false));
  }, [activeChat?.id]);

  // Scroll to bottom
  useEffect(() => {
    if (!loading) bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Search users
  useEffect(() => {
    if (searchQ.length < 2) { setSearchResults([]); return; }
    const t = setTimeout(() =>
      api.get("/users/search", { params: { q: searchQ } }).then(r => setSearchResults(r.data))
    , 300);
    return () => clearTimeout(t);
  }, [searchQ]);

  // WebSocket events
  useEffect(() => {
    const u1 = subscribe("new_message", (p: unknown) => {
      const msg = p as Message;
      if (msg.chat_id === activeChat?.id) {
        setMessages(prev => [...prev, msg]);
        setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
      }
      // Move chat to top
      setChats(prev => {
        const idx = prev.findIndex(c => c.id === msg.chat_id);
        if (idx < 0) return prev;
        const updated = [...prev];
        const [c] = updated.splice(idx, 1);
        return [c, ...updated];
      });
    });

    const u2 = subscribe("message_deleted", (p: unknown) => {
      const { chat_id, message_id } = p as { chat_id: string; message_id: string };
      if (chat_id === activeChat?.id)
        setMessages(prev => prev.map(m => m.id === message_id ? { ...m, deleted_for_everyone: true, content: null } : m));
    });

    const u3 = subscribe("message_edited", (p: unknown) => {
      const { chat_id, message_id, content } = p as { chat_id: string; message_id: string; content: string };
      if (chat_id === activeChat?.id)
        setMessages(prev => prev.map(m => m.id === message_id ? { ...m, content } : m));
    });

    const u4 = subscribe("typing", (p: unknown) => {
      const { chat_id, user_id, is_typing } = p as { chat_id: string; user_id: string; is_typing: boolean };
      if (chat_id !== activeChat?.id || user_id === user?.id) return;
      const name = activeChat?.members.find(m => m.user_id === user_id)?.display_name
                ?? activeChat?.members.find(m => m.user_id === user_id)?.username ?? "Someone";
      if (is_typing) { setTyping(name); }
      else setTyping(null);
    });

    const u5 = subscribe("presence", (p: unknown) => {
      const { user_id, online } = p as { user_id: string; online: boolean };
      setChats(prev => prev.map(c => ({
        ...c,
        members: c.members.map(m => m.user_id === user_id ? { ...m, online } : m)
      })));
    });

    return () => { u1(); u2(); u3(); u4(); u5(); };
  }, [activeChat?.id, subscribe, user?.id]);

  // Send message
  const sendMessage = useCallback(async () => {
    if (!text.trim() || !activeChat || sending) return;
    setSending(true);
    try {
      await api.post(`/chats/${activeChat.id}/messages`, { content: text.trim() });
      setText("");
    } catch { /* ignore */ }
    finally { setSending(false); }
  }, [text, activeChat, sending]);

  // Typing indicator
  const handleInput = (v: string) => {
    setText(v);
    if (!activeChat) return;
    send("typing", { chat_id: activeChat.id, is_typing: true });
    if (typingTimer.current) clearTimeout(typingTimer.current);
    typingTimer.current = setTimeout(() =>
      send("typing", { chat_id: activeChat.id, is_typing: false }), 2000);
  };

  // Open / start chat with a user
  const startChat = async (u: UserPublic) => {
    const r = await api.post("/chats/direct", { target_user_id: u.id });
    const chat: Chat = r.data;
    setChats(prev => prev.find(c => c.id === chat.id) ? prev : [chat, ...prev]);
    setActiveChat(chat);
    setSearchQ("");
    setSearchResults([]);
  };

  // Delete message
  const deleteMsg = async (msg: Message, forAll: boolean) => {
    await api.delete(`/chats/${activeChat!.id}/messages/${msg.id}`, { params: { for_everyone: forAll } });
    if (forAll)
      setMessages(prev => prev.map(m => m.id === msg.id ? { ...m, deleted_for_everyone: true, content: null } : m));
    else
      setMessages(prev => prev.filter(m => m.id !== msg.id));
  };

  const getOther = (c: Chat) => c.members.find(m => m.user_id !== user?.id);

  return (
    <div className="h-screen flex overflow-hidden bg-slate-950">

      {/* ── Sidebar ─────────────────────────────────────────────────── */}
      <div className="w-80 flex-shrink-0 flex flex-col bg-slate-900 border-r border-slate-800">

        {/* Header */}
        <div className="flex items-center justify-between px-4 py-4 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <Avatar name={user?.display_name ?? user?.username} size="sm" />
            <span className="text-sm font-semibold text-white">{user?.display_name ?? user?.username}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${connected ? "bg-emerald-400" : "bg-slate-600"}`} title={connected ? "Connected" : "Disconnected"} />
            <button onClick={logout} className="text-xs text-slate-400 hover:text-red-400 transition-colors px-2 py-1 rounded-lg hover:bg-slate-800">
              Logout
            </button>
          </div>
        </div>

        {/* Search */}
        <div className="px-4 py-3">
          <input
            value={searchQ}
            onChange={e => setSearchQ(e.target.value)}
            placeholder="🔍 Search users to chat…"
            className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2
                       text-sm text-white placeholder-slate-500 focus:outline-none focus:border-sky-500"
          />
        </div>

        {/* Search results */}
        {searchResults.length > 0 && (
          <div className="mx-4 mb-2 bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
            {searchResults.map(u => (
              <button key={u.id} onClick={() => startChat(u)}
                className="w-full flex items-center gap-3 px-3 py-2.5 hover:bg-slate-700 transition-colors text-left">
                <Avatar name={u.display_name ?? u.username} online={u.online} size="sm" />
                <div>
                  <p className="text-sm text-white">{u.display_name ?? u.username}</p>
                  <p className="text-xs text-slate-400">@{u.username}</p>
                </div>
              </button>
            ))}
          </div>
        )}

        {/* Chat list */}
        <div className="flex-1 overflow-y-auto px-2 space-y-0.5 py-1">
          {chats.length === 0 && (
            <p className="text-center text-slate-500 text-sm mt-8">No chats yet.<br/>Search for a user above.</p>
          )}
          {chats.map(c => {
            const other = getOther(c);
            const name = c.is_group ? c.name : (other?.display_name ?? other?.username ?? "Unknown");
            const isActive = activeChat?.id === c.id;
            return (
              <button key={c.id} onClick={() => setActiveChat(c)}
                className={`w-full flex items-center gap-3 px-3 py-3 rounded-xl transition-colors text-left ${
                  isActive ? "bg-sky-600/20 border border-sky-600/30" : "hover:bg-slate-800 border border-transparent"}`}>
                <Avatar name={name} online={!c.is_group ? other?.online : undefined} />
                <div className="min-w-0">
                  <p className="text-sm font-medium text-white truncate">{name}</p>
                  <p className="text-xs text-slate-400">{c.is_group ? `${c.members.length} members` : other?.online ? "Online" : "Offline"}</p>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* ── Chat Window ─────────────────────────────────────────────── */}
      <div className="flex-1 flex flex-col">
        {activeChat ? (() => {
          const other = getOther(activeChat);
          const name = activeChat.is_group ? activeChat.name : (other?.display_name ?? other?.username ?? "Chat");
          return (
            <>
              {/* Chat header */}
              <div className="flex items-center gap-3 px-4 py-3 bg-slate-900 border-b border-slate-800">
                <Avatar name={name} online={!activeChat.is_group ? other?.online : undefined} />
                <div>
                  <p className="font-semibold text-white text-sm">{name}</p>
                  <p className="text-xs text-slate-400">
                    {activeChat.is_group
                      ? `${activeChat.members.length} members`
                      : other?.online ? "🟢 Online" : "⚫ Offline"}
                  </p>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto px-4 py-3 space-y-1">
                {hasMore && (
                  <button onClick={() => {/* TODO: load more */}}
                    className="w-full text-xs text-sky-400 py-2">Load older messages</button>
                )}

                {loading ? (
                  <div className="flex items-center justify-center h-full text-slate-400 text-sm">Loading…</div>
                ) : messages.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-slate-500 text-sm">
                    <span className="text-4xl mb-3">👋</span>
                    Say hello to {name}!
                  </div>
                ) : (
                  messages.map(msg => {
                    const isMine = msg.sender?.id === user?.id;
                    return (
                      <div key={msg.id} className={`flex group ${isMine ? "justify-end" : "justify-start"}`}>
                        <div className={`relative max-w-xs md:max-w-md px-3 py-2 rounded-2xl text-sm shadow
                          ${isMine ? "bg-sky-600 text-white rounded-br-sm" : "bg-slate-800 text-slate-100 rounded-bl-sm"}`}>

                          {!isMine && activeChat.is_group && (
                            <p className="text-xs font-semibold text-sky-300 mb-0.5">
                              {msg.sender?.display_name ?? msg.sender?.username}
                            </p>
                          )}

                          {msg.deleted_for_everyone ? (
                            <p className="text-xs italic opacity-60">This message was deleted</p>
                          ) : (
                            <p className="whitespace-pre-wrap break-words">{msg.content}</p>
                          )}

                          <p className={`text-[10px] mt-0.5 text-right ${isMine ? "text-sky-100" : "text-slate-400"}`}>
                            {fmt(msg.created_at)}
                          </p>

                          {/* Delete menu */}
                          {!msg.deleted_for_everyone && (
                            <div className={`absolute top-0 ${isMine ? "-left-16" : "-right-16"}
                              hidden group-hover:flex gap-1 bg-slate-900 border border-slate-700
                              rounded-lg px-1 py-0.5 text-[10px]`}>
                              <button onClick={() => deleteMsg(msg, false)}
                                className="text-slate-400 hover:text-white px-1">🗑 Me</button>
                              {isMine && (
                                <button onClick={() => deleteMsg(msg, true)}
                                  className="text-red-400 hover:text-red-300 px-1">🗑 All</button>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })
                )}

                {typing && (
                  <div className="flex justify-start">
                    <div className="bg-slate-800 rounded-2xl px-3 py-2 text-xs text-slate-400 italic">
                      {typing} is typing…
                    </div>
                  </div>
                )}

                <div ref={bottomRef} />
              </div>

              {/* Input */}
              <div className="px-4 py-3 bg-slate-950 border-t border-slate-800 flex gap-2">
                <textarea
                  value={text}
                  onChange={e => handleInput(e.target.value)}
                  onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
                  placeholder="Type a message… (Enter to send)"
                  rows={1}
                  className="flex-1 bg-slate-800 border border-slate-700 rounded-2xl px-4 py-2.5
                             text-sm text-white placeholder-slate-500 focus:outline-none focus:border-sky-500
                             resize-none"
                  style={{ maxHeight: 120 }}
                />
                <button
                  onClick={sendMessage}
                  disabled={!text.trim() || sending}
                  className="px-4 py-2 bg-sky-500 hover:bg-sky-400 text-white rounded-2xl text-sm
                             font-medium transition-colors disabled:opacity-40">
                  Send
                </button>
              </div>
            </>
          );
        })() : (
          <div className="flex-1 flex flex-col items-center justify-center text-slate-500">
            <span className="text-6xl mb-4">💬</span>
            <p className="text-lg font-medium text-slate-400">FirstChat</p>
            <p className="text-sm mt-1">Select a chat or search for someone to start messaging</p>
          </div>
        )}
      </div>
    </div>
  );
}
