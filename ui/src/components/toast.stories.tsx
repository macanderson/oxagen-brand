import * as React from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import {
  ToastProvider,
  ToastViewport,
  useToast,
  type ToastAddOptions,
} from "./toast";
import { Button } from "./button";

const meta = {
  title: "Overlays/Toast",
  component: ToastProvider,
  // An open overlay portals to <body>, outside its story. On the Docs page
  // each story draws in its own frame, so the overlay stays with its story.
  parameters: { docs: { story: { inline: false, height: "360px" } } },
} satisfies Meta<typeof ToastProvider>;
export default meta;
type Story = StoryObj<typeof meta>;

const SAMPLES = {
  success: {
    title: "Policy saved",
    description: "The spend cap applies to the next run.",
    tone: "success",
  },
  info: {
    title: "Run queued",
    description: "Stella starts the review when a worker is free.",
    tone: "info",
  },
  warn: {
    title: "Approval needed",
    description: "The deploy step waits for an owner to approve it.",
    tone: "warn",
  },
  error: {
    title: "Run failed",
    description: "The workspace could not reach the model gateway.",
    tone: "error",
  },
} satisfies Record<string, ToastAddOptions>;

function Triggers() {
  const toast = useToast();
  return (
    <div className="flex flex-wrap gap-2">
      <Button onClick={() => toast.add(SAMPLES.success)}>Success</Button>
      <Button variant="outline" onClick={() => toast.add(SAMPLES.info)}>
        Info
      </Button>
      <Button variant="outline" onClick={() => toast.add(SAMPLES.warn)}>
        Warn
      </Button>
      <Button
        variant="destructive-outline"
        onClick={() => toast.add(SAMPLES.error)}
      >
        Error
      </Button>
    </div>
  );
}

/**
 * Adds toasts once on mount with `timeout: 0`, so the story holds still and
 * a screenshot taken at any moment shows the same stack.
 */
function Preset({ toasts }: { toasts: ToastAddOptions[] }) {
  const toast = useToast();
  const fired = React.useRef(false);
  React.useEffect(() => {
    if (fired.current) return;
    fired.current = true;
    for (const options of toasts) toast.add({ ...options, timeout: 0 });
  }, [toast, toasts]);
  return <Triggers />;
}

function Frame({ toasts }: { toasts?: ToastAddOptions[] }) {
  return (
    <ToastProvider>
      {toasts ? <Preset toasts={toasts} /> : <Triggers />}
      <ToastViewport />
    </ToastProvider>
  );
}

/** Press a button to add a toast. Each one lives 4200 ms. */
export const Playground: Story = {
  render: () => <Frame />,
};

export const Success: Story = {
  render: () => <Frame toasts={[SAMPLES.success]} />,
};

export const Info: Story = {
  render: () => <Frame toasts={[SAMPLES.info]} />,
};

export const Warn: Story = {
  render: () => <Frame toasts={[SAMPLES.warn]} />,
};

export const ErrorTone: Story = {
  name: "Error",
  render: () => <Frame toasts={[SAMPLES.error]} />,
};

/** A message with no description renders in the regular weight. */
export const TitleOnly: Story = {
  render: () => <Frame toasts={[{ title: "Link copied", tone: "success" }]} />,
};

export const WithAction: Story = {
  render: () => (
    <Frame
      toasts={[
        {
          title: "Key revoked",
          description: "Agents that used it stop at their next call.",
          tone: "warn",
          actionProps: { children: "Undo" },
        },
      ]}
    />
  ),
};

/** Three toasts. The newest sits in front. Hover the stack to open it. */
export const Stack: Story = {
  render: () => (
    <Frame toasts={[SAMPLES.info, SAMPLES.warn, SAMPLES.success]} />
  ),
};

/** Below 48rem the stack moves to the bottom centre. */
export const Phone: Story = {
  globals: { viewport: { value: "mobile1", isRotated: false } },
  render: () => (
    <Frame toasts={[SAMPLES.info, SAMPLES.warn, SAMPLES.success]} />
  ),
};
