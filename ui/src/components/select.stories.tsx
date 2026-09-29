import type { Meta, StoryObj } from "@storybook/react-vite";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectPopup,
  SelectItem,
  SelectGroup,
  SelectLabel,
} from "./select";

const meta = {
  title: "Forms/Select",
  component: Select,
  parameters: { layout: "centered" },
} satisfies Meta<typeof Select>;
export default meta;
type Story = StoryObj<typeof meta>;

const STATUSES = [
  { value: "any", label: "Any status" },
  { value: "running", label: "Running" },
  { value: "succeeded", label: "Succeeded" },
  { value: "failed", label: "Failed" },
  { value: "cancelled", label: "Cancelled" },
];

const MODELS = {
  anthropic: [
    { value: "opus", label: "Claude Opus" },
    { value: "sonnet", label: "Claude Sonnet" },
    { value: "haiku", label: "Claude Haiku" },
  ],
  openrouter: [
    { value: "kimi", label: "Kimi K2" },
    { value: "qwen", label: "Qwen3 Coder" },
  ],
};
const MODEL_ITEMS = [...MODELS.anthropic, ...MODELS.openrouter];

function StatusSelect({
  size,
  defaultOpen,
  disabled,
}: {
  size?: "sm" | "default" | "lg";
  defaultOpen?: boolean;
  disabled?: boolean;
}) {
  return (
    <Select
      items={STATUSES}
      defaultValue="running"
      defaultOpen={defaultOpen}
      disabled={disabled}
    >
      <SelectTrigger size={size} className="w-48" aria-label="Run status">
        <SelectValue />
      </SelectTrigger>
      <SelectPopup>
        {STATUSES.map((status) => (
          <SelectItem key={status.value} value={status.value}>
            {status.label}
          </SelectItem>
        ))}
      </SelectPopup>
    </Select>
  );
}

export const Closed: Story = {
  render: () => <StatusSelect />,
};

/** Open by default, so the surface, the rows and the checked mark show. */
export const Open: Story = {
  render: () => (
    <div className="min-h-72">
      <StatusSelect defaultOpen />
    </div>
  ),
};

export const Grouped: Story = {
  render: () => (
    <div className="min-h-80">
      <Select items={MODEL_ITEMS} defaultValue="sonnet" defaultOpen>
        <SelectTrigger className="w-56" aria-label="Model">
          <SelectValue />
        </SelectTrigger>
        <SelectPopup>
          <SelectGroup>
            <SelectLabel>Anthropic</SelectLabel>
            {MODELS.anthropic.map((model) => (
              <SelectItem key={model.value} value={model.value}>
                {model.label}
              </SelectItem>
            ))}
          </SelectGroup>
          <SelectGroup>
            <SelectLabel>OpenRouter</SelectLabel>
            {MODELS.openrouter.map((model) => (
              <SelectItem key={model.value} value={model.value}>
                {model.label}
              </SelectItem>
            ))}
          </SelectGroup>
        </SelectPopup>
      </Select>
    </div>
  ),
};

export const Disabled: Story = {
  render: () => <StatusSelect disabled />,
};

export const Sizes: Story = {
  render: () => (
    <div className="flex flex-col items-start gap-3">
      <StatusSelect size="sm" />
      <StatusSelect />
      <StatusSelect size="lg" />
    </div>
  ),
};
