// @vitest-environment jsdom
/**
 * pwa/install-prompt.js is a plain browser script every Oxagen frontend loads.
 * It is evaluated here with a stand-in `module`, the one way to reach its
 * functions without a bundler, whatever the package's module type.
 */
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

interface Api {
  COOKIE: string;
  dismissed(doc: Document): boolean;
  remember(doc: Document, loc: { protocol: string }): void;
  standalone(win: Window): boolean;
  ios(nav: Partial<Navigator>): boolean;
  eligible(win: Window, doc: Document): boolean;
  start(win: Window, doc: Document, script: HTMLScriptElement | null): void;
}

const SRC = readFileSync(
  resolve(dirname(fileURLToPath(import.meta.url)), "../../../pwa/install-prompt.js"),
  "utf8",
);

function load(): Api {
  const mod = { exports: {} as Api };
  new Function("module", SRC)(mod);
  return mod.exports;
}

let media: Record<string, boolean> = {};

/** Media queries answer from `matches` for the rest of the test. */
function withMedia(matches: Record<string, boolean>) {
  media = matches;
}

/**
 * A fresh window per test: its own event target, so a listener one test's
 * `start` adds cannot draw a card in the next.
 */
function fakeWindow(userAgent = "Mozilla/5.0 (Linux; Android 15; Pixel 9)"): Window {
  return Object.assign(new EventTarget(), {
    matchMedia: (q: string) => ({ matches: !!media[q], media: q }),
    navigator: { userAgent, maxTouchPoints: 5 },
    location: { protocol: "https:" },
    setTimeout: (fn: () => void, ms: number) => window.setTimeout(fn, ms),
  }) as unknown as Window;
}

const TOUCH = { "(pointer: coarse)": true };

function clearCookies() {
  for (const part of document.cookie.split(";")) {
    const name = part.split("=")[0]?.trim();
    if (name) document.cookie = `${name}=; Max-Age=0; Path=/`;
  }
}

function card() {
  return document.querySelector("[data-ox-install-prompt]");
}

function install(outcome: "accepted" | "dismissed") {
  const e = new Event("beforeinstallprompt", { cancelable: true }) as Event & {
    prompt: () => void;
    userChoice: Promise<{ outcome: string }>;
  };
  e.prompt = vi.fn();
  e.userChoice = Promise.resolve({ outcome });
  return e;
}

beforeEach(() => {
  clearCookies();
  media = {};
  document.body.innerHTML = "";
});

afterEach(() => {
  vi.restoreAllMocks();
  vi.useRealTimers();
});

describe("the cookie", () => {
  it("is absent on a first visit and present once remembered", () => {
    const api = load();
    expect(api.dismissed(document)).toBe(false);
    api.remember(document, { protocol: "http:" });
    expect(api.dismissed(document)).toBe(true);
    expect(document.cookie).toContain(`${api.COOKIE}=dismissed`);
  });

  it("is forgotten when cookies are cleared, so the card can show again", () => {
    const api = load();
    api.remember(document, { protocol: "http:" });
    clearCookies();
    withMedia(TOUCH);
    expect(api.eligible(fakeWindow(), document)).toBe(true);
  });
});

describe("who is offered the card", () => {
  it("offers it on a touch device on a first visit", () => {
    withMedia(TOUCH);
    expect(load().eligible(fakeWindow(), document)).toBe(true);
  });

  it("does not offer it on a device with a mouse", () => {
    withMedia({});
    expect(load().eligible(fakeWindow(), document)).toBe(false);
  });

  it("does not offer it inside the installed app", () => {
    withMedia({ ...TOUCH, "(display-mode: standalone)": true });
    expect(load().eligible(fakeWindow(), document)).toBe(false);
  });

  it("recognises an iPhone, and an iPad that reports a Mac", () => {
    const api = load();
    expect(api.ios({ userAgent: "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X)" })).toBe(true);
    expect(api.ios({ userAgent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)", maxTouchPoints: 5 })).toBe(true);
    expect(api.ios({ userAgent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)", maxTouchPoints: 0 })).toBe(false);
    expect(api.ios({ userAgent: "Mozilla/5.0 (Linux; Android 15; Pixel 9)" })).toBe(false);
  });
});

describe("on Android and Chromium", () => {
  it("shows the card when the browser says the site is installable", () => {
    withMedia(TOUCH);
    const win = fakeWindow();
    load().start(win, document, null);
    const e = install("accepted");
    win.dispatchEvent(e);
    expect(e.defaultPrevented).toBe(true);
    expect(card()).not.toBeNull();
    expect(card()?.shadowRoot?.textContent).toContain("Add Oxagen to your home screen");
  });

  it("opens the browser's dialog and retires the card on either answer", async () => {
    withMedia(TOUCH);
    const api = load();
    const win = fakeWindow();
    api.start(win, document, null);
    const e = install("dismissed");
    win.dispatchEvent(e);
    (card()?.shadowRoot?.querySelector('[data-act="install"]') as HTMLButtonElement).click();
    expect(e.prompt).toHaveBeenCalledOnce();
    await new Promise((settle) => setTimeout(settle, 0));
    expect(card()).toBeNull();
    expect(api.dismissed(document)).toBe(true);
  });

  it("sets the cookie when closed, and a later visit shows nothing", () => {
    withMedia(TOUCH);
    const api = load();
    const win = fakeWindow();
    api.start(win, document, null);
    win.dispatchEvent(install("accepted"));
    (card()?.shadowRoot?.querySelector('[data-act="dismiss"]') as HTMLButtonElement).click();
    expect(card()).toBeNull();
    expect(api.dismissed(document)).toBe(true);

    const later = fakeWindow();
    load().start(later, document, null);
    later.dispatchEvent(install("accepted"));
    expect(card()).toBeNull();
  });

  it("closes on Escape", () => {
    withMedia(TOUCH);
    const win = fakeWindow();
    load().start(win, document, null);
    win.dispatchEvent(install("accepted"));
    document.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape" }));
    expect(card()).toBeNull();
  });
});

describe("on iPhone and iPad Safari", () => {
  it("shows the Share instructions after a short wait, with no install button", () => {
    vi.useFakeTimers();
    withMedia(TOUCH);
    load().start(fakeWindow("Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) Safari/604.1"), document, null);
    expect(card()).toBeNull();
    vi.advanceTimersByTime(3000);
    const root = card()?.shadowRoot;
    expect(root?.textContent).toContain("Add to Home Screen");
    expect(root?.querySelector('[data-act="install"]')).toBeNull();
  });
});

describe("text from the script tag", () => {
  it("replaces the default strings and draws the icon", () => {
    withMedia(TOUCH);
    const script = document.createElement("script");
    script.dataset.title = "Ajouter Oxagen";
    script.dataset.install = "Ajouter";
    script.dataset.icon = "/pwa/icon-192.png";
    const win = fakeWindow();
    load().start(win, document, script);
    win.dispatchEvent(install("accepted"));
    const root = card()?.shadowRoot;
    expect(root?.textContent).toContain("Ajouter Oxagen");
    expect(root?.querySelector("img")?.getAttribute("src")).toBe("/pwa/icon-192.png");
  });
});
