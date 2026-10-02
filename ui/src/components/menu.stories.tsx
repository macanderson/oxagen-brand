import type { Meta, StoryObj } from "@storybook/react-vite";
import {
  ArchiveIcon,
  CopyIcon,
  GearIcon,
  PencilLineIcon,
  RobotIcon,
  SignOutIcon,
  TerminalWindowIcon,
  TrashIcon,
  UserIcon,
} from "@phosphor-icons/react";
import {
  Menu,
  MenuTrigger,
  MenuPopup,
  MenuItem,
  MenuCheckboxItem,
  MenuGroup,
  MenuGroupLabel,
  MenuRadioGroup,
  MenuRadioItem,
  MenuSeparator,
  MenuShortcut,
  MenuSub,
  MenuSubTrigger,
  MenuSubPopup,
} from "./menu";
import { Button } from "./button";

/**
 * Every story opens by default, so the surface, rows and marks show in the
 * catalog without a click.
 */
const meta = {
  title: "Overlays/Menu",
  component: Menu,
  // An open overlay portals to <body>, outside its story. On the Docs page
  // each story draws in its own frame, so the overlay stays with its story.
  parameters: {
    layout: "centered",
    docs: { story: { inline: false, height: "400px" } },
  },
  decorators: [
    (Story) => (
      <div className="flex min-h-80 items-start justify-center">
        <Story />
      </div>
    ),
  ],
} satisfies Meta<typeof Menu>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Plain: Story = {
  render: () => (
    <Menu defaultOpen>
      <MenuTrigger render={<Button variant="outline">Run actions</Button>} />
      <MenuPopup>
        <MenuItem onClick={() => {}}>Open transcript</MenuItem>
        <MenuItem onClick={() => {}}>Copy run link</MenuItem>
        <MenuItem onClick={() => {}}>Compare with last run</MenuItem>
        <MenuSeparator />
        <MenuItem onClick={() => {}}>Archive run</MenuItem>
      </MenuPopup>
    </Menu>
  ),
};

export const GroupLabels: Story = {
  render: () => (
    <Menu defaultOpen>
      <MenuTrigger render={<Button variant="outline">Account</Button>} />
      <MenuPopup>
        <MenuGroup>
          <MenuGroupLabel>Signed in as mac</MenuGroupLabel>
          <MenuItem onClick={() => {}}>
            Profile
            <MenuShortcut>⇧⌘P</MenuShortcut>
          </MenuItem>
          <MenuItem onClick={() => {}}>
            Settings
            <MenuShortcut>⌘,</MenuShortcut>
          </MenuItem>
        </MenuGroup>
        <MenuSeparator />
        <MenuGroup>
          <MenuGroupLabel>Workspace</MenuGroupLabel>
          <MenuItem onClick={() => {}}>Members</MenuItem>
          <MenuItem onClick={() => {}}>Billing</MenuItem>
        </MenuGroup>
      </MenuPopup>
    </Menu>
  ),
};

export const IconsAndDisabled: Story = {
  render: () => (
    <Menu defaultOpen>
      <MenuTrigger render={<Button variant="outline">Agent</Button>} />
      <MenuPopup className="w-60">
        <MenuItem onClick={() => {}}>
          <PencilLineIcon />
          Rename agent
        </MenuItem>
        <MenuItem onClick={() => {}}>
          <CopyIcon />
          Duplicate
          <MenuShortcut>⌘D</MenuShortcut>
        </MenuItem>
        <MenuItem onClick={() => {}}>
          <TerminalWindowIcon />
          Open last run
        </MenuItem>
        <MenuItem disabled>
          <ArchiveIcon />
          Archive while running
        </MenuItem>
        <MenuSeparator />
        <MenuItem variant="destructive" onClick={() => {}}>
          <TrashIcon />
          Delete agent
        </MenuItem>
      </MenuPopup>
    </Menu>
  ),
};

export const CheckboxAndRadio: Story = {
  render: () => (
    <Menu defaultOpen>
      <MenuTrigger render={<Button variant="outline">View</Button>} />
      <MenuPopup className="w-60">
        <MenuGroup>
          <MenuGroupLabel>Show</MenuGroupLabel>
          <MenuCheckboxItem defaultChecked>Tool calls</MenuCheckboxItem>
          <MenuCheckboxItem defaultChecked>Token counts</MenuCheckboxItem>
          <MenuCheckboxItem>Cache hits</MenuCheckboxItem>
        </MenuGroup>
        <MenuSeparator />
        <MenuRadioGroup defaultValue="cost">
          <MenuGroupLabel>Sort runs by</MenuGroupLabel>
          <MenuRadioItem value="recent">Most recent</MenuRadioItem>
          <MenuRadioItem value="cost">Highest spend</MenuRadioItem>
          <MenuRadioItem value="duration">Longest duration</MenuRadioItem>
        </MenuRadioGroup>
      </MenuPopup>
    </Menu>
  ),
};

export const Submenu: Story = {
  render: () => (
    <Menu defaultOpen>
      <MenuTrigger render={<Button variant="outline">Mac Anderson</Button>} />
      <MenuPopup className="w-56">
        <MenuItem onClick={() => {}}>
          <UserIcon />
          Profile
        </MenuItem>
        <MenuSub defaultOpen>
          <MenuSubTrigger>
            <RobotIcon />
            Assign to agent
          </MenuSubTrigger>
          <MenuSubPopup className="w-48">
            <MenuItem onClick={() => {}}>Triage bot</MenuItem>
            <MenuItem onClick={() => {}}>Release captain</MenuItem>
            <MenuItem onClick={() => {}}>Docs writer</MenuItem>
          </MenuSubPopup>
        </MenuSub>
        <MenuItem onClick={() => {}}>
          <GearIcon />
          Settings
        </MenuItem>
        <MenuSeparator />
        <MenuItem onClick={() => {}}>
          <SignOutIcon />
          Sign out
        </MenuItem>
      </MenuPopup>
    </Menu>
  ),
};
