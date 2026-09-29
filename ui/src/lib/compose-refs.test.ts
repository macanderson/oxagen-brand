// compose-refs.test.ts: unit tests for composeRefs().
//
// React 19 calls the cleanup a callback ref returns in place of calling the
// ref with null. These tests play React's part: attach, then run the cleanup.

import { createRef, type RefCallback } from "react";
import { describe, expect, it, vi } from "vitest";
import { composeRefs } from "./compose-refs";

const node = { id: "popup" };

function attach<T>(ref: RefCallback<T>, value: T): () => void {
  const cleanup = ref(value);
  if (typeof cleanup !== "function") throw new Error("expected a cleanup");
  return cleanup;
}

describe("composeRefs", () => {
  it("sets an object ref and clears it on cleanup", () => {
    const ref = createRef<typeof node>();
    const cleanup = attach(composeRefs<typeof node>(ref), node);
    expect(ref.current).toBe(node);
    cleanup();
    expect(ref.current).toBeNull();
  });

  it("calls a callback ref with the node, then with null when it returns nothing", () => {
    const ref = vi.fn();
    const cleanup = attach(composeRefs<typeof node>(ref), node);
    expect(ref).toHaveBeenLastCalledWith(node);
    cleanup();
    expect(ref).toHaveBeenLastCalledWith(null);
    expect(ref).toHaveBeenCalledTimes(2);
  });

  it("runs the cleanup a callback ref returns, and does not call it with null", () => {
    const disconnect = vi.fn();
    const ref = vi.fn(() => disconnect);
    const cleanup = attach(composeRefs<typeof node>(ref), node);
    cleanup();
    expect(disconnect).toHaveBeenCalledTimes(1);
    expect(ref).toHaveBeenCalledTimes(1);
    expect(ref).toHaveBeenCalledWith(node);
  });

  it("sets every ref it is given and skips null and undefined", () => {
    const object = createRef<typeof node>();
    const callback = vi.fn();
    const cleanup = attach(
      composeRefs<typeof node>(object, null, undefined, callback),
      node,
    );
    expect(object.current).toBe(node);
    expect(callback).toHaveBeenCalledWith(node);
    cleanup();
    expect(object.current).toBeNull();
    expect(callback).toHaveBeenLastCalledWith(null);
  });
});
