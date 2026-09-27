/**
 * Toast — shadcn-shaped wrapper over Base UI's imperative toast system.
 *
 * Mount once at the app root:
 *   <ToastProvider><App /><ToastViewport /></ToastProvider>
 *
 * Then enqueue toasts from anywhere under the provider:
 *   const toast = useToast();
 *   toast.add({ title: "Saved", description: "Your changes are live." });
 */
declare const ToastProvider: import("react").FC<import("@base-ui/react").ToastProviderProps>;
/** Returns the Base UI toast manager (`.add`, `.update`, `.close`, …). */
declare function useToast(): import("@base-ui/react").UseToastManagerReturnValue<any>;
declare function ToastViewport({ className }: {
    className?: string;
}): import("react/jsx-runtime").JSX.Element;
export { ToastProvider, ToastViewport, useToast };
