import type { Meta, StoryObj } from "@storybook/react-vite";
import { PlusIcon, RocketLaunchIcon } from "@phosphor-icons/react";
import { Button } from "./button";

const meta = {
  title: "Primitives/Button",
  component: Button,
  argTypes: {
    variant: {
      control: "select",
      options: [
        "primary",
        "default",
        "secondary",
        "outline",
        "ghost",
        "destructive",
        "destructive-outline",
        "link",
        "gradient",
      ],
    },
    size: {
      control: "select",
      options: [
        "xs",
        "sm",
        "default",
        "lg",
        "xl",
        "icon",
        "icon-sm",
        "icon-lg",
      ],
    },
    disabled: { control: "boolean" },
    loading: { control: "boolean" },
  },
  args: { children: "Run agent", variant: "default", size: "default" },
} satisfies Meta<typeof Button>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Playground: Story = {};

// One story per variant.

export const Primary: Story = {
  args: { variant: "primary", children: "Approve run" },
};

export const Default: Story = {
  args: { variant: "default", children: "Run agent" },
};

export const Secondary: Story = {
  args: { variant: "secondary", children: "View transcript" },
};

export const Outline: Story = {
  args: { variant: "outline", children: "Open workspace" },
};

export const Ghost: Story = {
  args: { variant: "ghost", children: "Skip step" },
};

export const Destructive: Story = {
  args: { variant: "destructive", children: "Revoke key" },
};

export const DestructiveOutline: Story = {
  args: { variant: "destructive-outline", children: "Stop run" },
};

export const Link: Story = {
  args: { variant: "link", children: "Read the policy" },
};

export const Gradient: Story = {
  args: { variant: "gradient", children: "Start trial" },
};

// One story per size.

export const SizeXs: Story = {
  name: "Size xs",
  args: { size: "xs", children: "Retry" },
};

export const SizeSm: Story = {
  name: "Size sm",
  args: { size: "sm", children: "Retry" },
};

export const SizeDefault: Story = {
  name: "Size default",
  args: { size: "default", children: "Retry" },
};

export const SizeLg: Story = {
  name: "Size lg",
  args: { size: "lg", children: "Retry" },
};

export const SizeXl: Story = {
  name: "Size xl",
  args: { size: "xl", children: "Retry" },
};

export const SizeIcon: Story = {
  name: "Size icon",
  args: {
    size: "icon",
    variant: "outline",
    "aria-label": "New run",
    children: <PlusIcon aria-hidden="true" />,
  },
};

export const SizeIconSm: Story = {
  name: "Size icon-sm",
  args: {
    size: "icon-sm",
    variant: "outline",
    "aria-label": "New run",
    children: <PlusIcon aria-hidden="true" />,
  },
};

export const SizeIconLg: Story = {
  name: "Size icon-lg",
  args: {
    size: "icon-lg",
    variant: "outline",
    "aria-label": "New run",
    children: <PlusIcon aria-hidden="true" />,
  },
};

// States.

export const WithIcon: Story = {
  args: {
    children: "Deploy",
    startIcon: <RocketLaunchIcon aria-hidden="true" />,
  },
};

export const Disabled: Story = {
  args: { disabled: true, children: "Approve run" },
};

export const DisabledWithTooltip: Story = {
  args: {
    disabled: true,
    children: "Publish",
    disabledTooltip: "You need the Editor role to publish.",
  },
};

export const Loading: Story = {
  args: { loading: true, children: "Saving policy" },
};
