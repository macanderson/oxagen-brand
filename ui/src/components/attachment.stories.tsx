import type { Meta, StoryObj } from "@storybook/react-vite";
import { AttachmentCard, type AttachmentFile } from "./attachment";

/**
 * One file in the composer: a media tile, the file's name, kind, and size, and
 * a remove button. It shimmers while the file uploads.
 */
const meta = {
  title: "Forms/Attachment",
  component: AttachmentCard,
  args: {
    file: {
      id: "q3-incident-review",
      name: "q3-incident-review.pdf",
      size: 2516582,
    },
    onRemove: () => {},
  },
} satisfies Meta<typeof AttachmentCard>;
export default meta;
type Story = StoryObj<typeof meta>;

const KINDS: AttachmentFile[] = [
  { id: "pdf", name: "q3-incident-review.pdf", size: 2516582 },
  { id: "png", name: "latency-dashboard.png", size: 348160 },
  { id: "md", name: "refund-runbook.md", size: 9216 },
  { id: "ts", name: "refund-policy.ts", size: 4812 },
  { id: "zip", name: "audit-export.zip", size: 18874368 },
];

export const Default: Story = {};

/** The name shimmers and the line under it reads "Uploading". */
export const Uploading: Story = {
  args: {
    file: {
      id: "refund-runbook",
      name: "refund-runbook.md",
      size: 9216,
      state: "uploading",
    },
  },
};

export const Failed: Story = {
  args: {
    file: {
      id: "audit-export",
      name: "audit-export.zip",
      size: 18874368,
      state: "error",
    },
  },
};

/** A sent turn shows its cards with no remove button. */
export const ReadOnly: Story = {
  args: { onRemove: undefined },
};

/** One card for each kind the tile knows, and one it does not. */
export const Kinds: Story = {
  render: (args) => (
    <div className="flex max-w-[520px] flex-wrap gap-2">
      {KINDS.map((file) => (
        <AttachmentCard key={file.id} file={file} onRemove={args.onRemove} />
      ))}
    </div>
  ),
};
