const BASE = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}`
  : "/api";

export interface User {
  id: number;
  name: string;
  age: number;
  gender: string;
  bio: string;
  instagram: string;
  linkedin: string;
  spotify: string;
  phone_verified: boolean;
}

export interface Event {
  id: number;
  external_url: string;
  title: string;
  category: string;
  location: string;
  starts_at: string | null;
}

export interface Group {
  id: number;
  event_id: number;
  vibe: string;
  status: string;
  event: Event;
  members: { user: User }[];
}

export interface MatchResult {
  request: { id: number; status: string; group_id: number | null };
  matched: boolean;
  group: Group | null;
}

export interface ChatMessage {
  id: number;
  group_id: number;
  user_id: number;
  body: string;
  created_at: string;
}

async function req<T>(path: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(BASE + path, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

export const api = {
  createUser: (data: Partial<User>) =>
    req<User>("/users", { method: "POST", body: JSON.stringify(data) }),
  createEvent: (data: Partial<Event>) =>
    req<Event>("/events", { method: "POST", body: JSON.stringify(data) }),
  createMatchRequest: (data: Record<string, unknown>) =>
    req<MatchResult>("/match-requests", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  getMatchRequest: (id: number) => req<MatchResult>(`/match-requests/${id}`),
  getGroup: (id: number) => req<Group>(`/groups/${id}`),
  getMessages: (id: number) => req<ChatMessage[]>(`/groups/${id}/messages`),
  postMessage: (id: number, user_id: number, body: string) =>
    req<ChatMessage>(`/groups/${id}/messages`, {
      method: "POST",
      body: JSON.stringify({ user_id, body }),
    }),
};
