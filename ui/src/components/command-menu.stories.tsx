import type { Meta, StoryObj } from "@storybook/react-vite";
import {
  CurrencyDollarIcon,
  EnvelopeSimpleIcon,
  GearIcon,
  KeyIcon,
  LightningIcon,
  ListChecksIcon,
  PauseIcon,
  PlugsConnectedIcon,
  PlusIcon,
  RobotIcon,
  ShieldCheckIcon,
  SteeringWheelIcon,
  UserCircleIcon,
  WrenchIcon,
} from "@phosphor-icons/react";
import {
  CommandMenu,
  CommandMenuTrigger,
  type CommandMenuCommandGroup,
} from "./command-menu";

const meta = {
  title: "Overlays/CommandMenu",
  component: CommandMenu,
  // An open overlay portals to <body>, outside its story. On the Docs page
  // each story draws in its own frame, so the overlay stays with its story.
  parameters: { docs: { story: { inline: false, height: "520px" } } },
  args: { groups: [] },
} satisfies Meta<typeof CommandMenu>;
export default meta;
type Story = StoryObj<typeof meta>;

// The mockup's three groups, trimmed to what a workspace admin sees.
const GROUPS: CommandMenuCommandGroup[] = [
  {
    label: "Go to",
    items: [
      { value: "work", label: "Work", icon: <ListChecksIcon /> },
      { value: "runs", label: "Runs", icon: <LightningIcon /> },
      { value: "agents", label: "Agents", icon: <RobotIcon /> },
      { value: "steering", label: "Steering", icon: <SteeringWheelIcon /> },
      { value: "tools", label: "Tools", icon: <WrenchIcon /> },
      {
        value: "spend",
        label: "Spend",
        icon: <CurrencyDollarIcon />,
        keywords: ["billing", "cost"],
      },
      { value: "settings", label: "Workspace settings", icon: <GearIcon /> },
    ],
  },
  {
    label: "Create",
    items: [
      { value: "new-work", label: "New work item", icon: <PlusIcon /> },
      {
        value: "connect",
        label: "Connect an agent",
        icon: <PlugsConnectedIcon />,
        detail: "Claude Code, Codex or Stella",
      },
      { value: "invite", label: "Invite a person", icon: <EnvelopeSimpleIcon /> },
      { value: "api-key", label: "New API key", icon: <KeyIcon /> },
    ],
  },
  {
    label: "Actions",
    items: [
      { value: "pause", label: "Pause every live run", icon: <PauseIcon /> },
      { value: "mandate", label: "Grant a mandate", icon: <ShieldCheckIcon /> },
      { value: "avatar", label: "Change your avatar", icon: <UserCircleIcon /> },
    ],
  },
];

/** The top bar's search button. Press it, or Cmd+K, to open the menu. */
export const Default: Story = {
  render: () => (
    <CommandMenu groups={GROUPS}>
      <CommandMenuTrigger />
    </CommandMenu>
  ),
};

/** Every group, open with nothing typed. The first row is highlighted. */
export const Grouped: Story = {
  render: () => (
    <div className="min-h-[560px]">
      <CommandMenu groups={GROUPS} defaultOpen>
        <CommandMenuTrigger />
      </CommandMenu>
    </div>
  ),
};

/** A query that matches rows in two groups. */
export const OpenWithResults: Story = {
  render: () => (
    <div className="min-h-[560px]">
      <CommandMenu groups={GROUPS} defaultOpen defaultQuery="agent">
        <CommandMenuTrigger />
      </CommandMenu>
    </div>
  ),
};

/** A query that matches nothing. */
export const NoResults: Story = {
  render: () => (
    <div className="min-h-[560px]">
      <CommandMenu groups={GROUPS} defaultOpen defaultQuery="billing export">
        <CommandMenuTrigger />
      </CommandMenu>
    </div>
  ),
};
