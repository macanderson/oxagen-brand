import type * as React from "react";

/**
 * One callback ref that sets every ref it is given, for a component that
 * keeps its own ref to a node and forwards the caller's too.
 *
 * It returns React 19's ref cleanup. A callback ref that returned its own
 * cleanup gets that cleanup back, so an observer it started is stopped. One
 * that returned nothing is called with `null`, and an object ref is cleared.
 * Build it with `useMemo` over the refs, so React does not detach and
 * reattach the node on every render.
 */
export function composeRefs<T>(
  ...refs: readonly (React.Ref<T> | undefined)[]
): React.RefCallback<T> {
  return (node) => {
    const cleanups = refs.map((ref): (() => void) | undefined => {
      if (typeof ref === "function") {
        const callback = ref;
        const cleanup = callback(node);
        return typeof cleanup === "function" ? cleanup : () => callback(null);
      }
      if (ref) {
        const object = ref;
        object.current = node;
        return () => {
          object.current = null;
        };
      }
      return undefined;
    });
    return () => {
      for (const cleanup of cleanups) cleanup?.();
    };
  };
}
