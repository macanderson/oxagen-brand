import type { Meta, StoryObj } from "@storybook/react-vite";
import { TONE_BADGE_TONES, ToneBadge, type ToneBadgeTone } from "./tone-badge";

/**
 * A badge for a record's state. It draws each state with a shape as well as a
 * colour.
 */
const meta = {
  title: "Primitives/ToneBadge",
  component: ToneBadge,
  argTypes: {
    tone: { control: "select", options: TONE_BADGE_TONES },
    dot: { control: "select", options: [true, false, "pulse"] },
  },
  args: { tone: "allowed", children: "Allowed" },
} satisfies Meta<typeof ToneBadge>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Playground: Story = {};

/** The word each state reads as on a run. */
const WORD: Record<ToneBadgeTone, string> = {
  allowed: "Allowed",
  approval: "Needs approval",
  denied: "Denied",
  proven: "Proven",
  failed: "Failed",
  critical: "Critical",
  quiet: "Draft",
};

export const EveryTone: Story = {
  render: () => (
    <div className="flex flex-wrap items-center gap-2">
      {TONE_BADGE_TONES.map((tone) => (
        <ToneBadge key={tone} tone={tone}>
          {WORD[tone]}
        </ToneBadge>
      ))}
    </div>
  ),
};

export const WithoutDot: Story = {
  render: () => (
    <div className="flex flex-wrap items-center gap-2">
      {TONE_BADGE_TONES.map((tone) => (
        <ToneBadge key={tone} tone={tone} dot={false}>
          {WORD[tone]}
        </ToneBadge>
      ))}
    </div>
  ),
};

export const Pulsing: Story = {
  render: () => (
    <div className="flex flex-wrap items-center gap-2">
      <ToneBadge tone="allowed" dot="pulse">
        Running
      </ToneBadge>
      <ToneBadge tone="approval" dot="pulse">
        Waiting on approval
      </ToneBadge>
    </div>
  ),
};

export const Tier: Story = {
  render: () => (
    <div className="flex flex-wrap items-center gap-2">
      <ToneBadge tone="quiet" dot={false} mono>
        harness
      </ToneBadge>
      <ToneBadge tone="quiet" dot={false} mono>
        gateway
      </ToneBadge>
      <ToneBadge tone="proven" dot={false} mono>
        kernel
      </ToneBadge>
    </div>
  ),
};

const AGENTS: [string, ToneBadgeTone][] = [
  ["release-bot", "allowed"],
  ["schema-migrator", "approval"],
  ["dependency-updater", "denied"],
  ["audit-writer", "proven"],
];

export const InATable: Story = {
  render: () => (
    <table className="w-[480px] border-collapse text-[13px]">
      <tbody>
        {AGENTS.map(([agent, tone]) => (
          <tr key={agent} className="border-b border-border last:border-b-0">
            <td className="px-3 py-2 font-mono text-xs text-foreground">
              {agent}
            </td>
            <td className="px-3 py-2 text-right">
              <ToneBadge tone={tone}>{WORD[tone]}</ToneBadge>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  ),
};
