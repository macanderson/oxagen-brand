import * as React from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import type { AttachmentFile } from "./attachment";
import { Composer, ComposerSentTurn } from "./composer";

const PDF: AttachmentFile = {
  id: "q3-incident-review",
  name: "q3-incident-review.pdf",
  size: 2516582,
};
const PNG: AttachmentFile = {
  id: "latency-dashboard",
  name: "latency-dashboard.png",
  size: 348160,
};
const MD_UPLOADING: AttachmentFile = {
  id: "refund-runbook",
  name: "refund-runbook.md",
  size: 9216,
  state: "uploading",
};

const meta = {
  title: "Forms/Composer",
  component: Composer,
  decorators: [
    (Story) => (
      <div className="w-full max-w-[560px]">
        <Story />
      </div>
    ),
  ],
  args: {
    toolbar: "Stella on the refunds workspace",
    // No-op callbacks, so each card shows its remove button.
    onFilesAdd: () => {},
    onFileRemove: () => {},
    onSend: () => {},
  },
} satisfies Meta<typeof Composer>;
export default meta;
type Story = StoryObj<typeof meta>;

let nextId = 0;

/**
 * Holds the files in story state and fakes a 1.2 second upload for each one.
 * A file already attached, by name and size, is not added twice.
 */
function LiveComposer() {
  const [files, setFiles] = React.useState<AttachmentFile[]>([]);
  const [sent, setSent] = React.useState<
    { id: number; text: string; files: AttachmentFile[] }[]
  >([]);
  const timers = React.useRef<number[]>([]);

  React.useEffect(
    () => () => {
      for (const timer of timers.current) window.clearTimeout(timer);
    },
    [],
  );

  function onFilesAdd(added: File[]) {
    const fresh = added.filter(
      (file) =>
        !files.some(
          (known) => known.name === file.name && known.size === file.size,
        ),
    );
    const cards = fresh.map<AttachmentFile>((file) => ({
      id: `upload-${nextId++}`,
      name: file.name,
      size: file.size,
      state: "uploading",
    }));
    if (cards.length === 0) return;
    setFiles((current) => [...current, ...cards]);
    for (const card of cards) {
      timers.current.push(
        window.setTimeout(() => {
          setFiles((now) =>
            now.map<AttachmentFile>((file) =>
              file.id === card.id ? { ...file, state: "done" } : file,
            ),
          );
        }, 1200),
      );
    }
  }

  return (
    <div className="flex flex-col gap-4">
      {sent.map((turn) => (
        <ComposerSentTurn key={turn.id} files={turn.files}>
          {turn.text}
        </ComposerSentTurn>
      ))}
      <Composer
        files={files}
        onFilesAdd={onFilesAdd}
        onFileRemove={(removed) =>
          setFiles((current) => current.filter((file) => file.id !== removed.id))
        }
        onSend={(text) => {
          setSent((turns) => [...turns, { id: nextId++, text, files }]);
          setFiles([]);
        }}
        toolbar="Stella on the refunds workspace"
      />
    </div>
  );
}

/** Attach, drop, or paste files. Each one uploads for 1.2 seconds. */
export const Playground: Story = {
  render: () => <LiveComposer />,
};

export const Empty: Story = {};

export const OneFile: Story = {
  args: { files: [PDF] },
};

export const SeveralFiles: Story = {
  args: {
    files: [PDF, PNG, { ...MD_UPLOADING, state: "done" }],
    defaultValue: "Compare the incident review with the dashboard.",
  },
};

/** The title shimmers while a file uploads, and Send waits for it. */
export const Uploading: Story = {
  args: {
    files: [PDF, MD_UPLOADING],
    defaultValue: "Check the runbook against the review.",
  },
};

/** The input takes a dashed gold border while files are dragged over it. */
export const DropTargetActive: Story = {
  args: { dropActive: true, files: [PDF] },
};

/** A question after it is sent. Its cards have no remove button. */
export const SentTurn: Story = {
  render: () => (
    <div className="flex flex-col">
      <ComposerSentTurn files={[PDF, PNG]}>
        What changed in the refund path after the Q3 incident?
      </ComposerSentTurn>
    </div>
  ),
};

/** Below 48rem the cards wrap and the input text grows to 16px. */
export const Phone: Story = {
  globals: { viewport: { value: "mobile1", isRotated: false } },
  args: { files: [PDF, PNG, MD_UPLOADING] },
};
