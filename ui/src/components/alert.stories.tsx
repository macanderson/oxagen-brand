import type { ComponentProps } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import {
  CheckCircleIcon,
  InfoIcon,
  WarningIcon,
  XCircleIcon,
} from "@phosphor-icons/react";
import { Alert, AlertTitle, AlertDescription } from "./alert";

const meta = {
  title: "Primitives/Alert",
  component: Alert,
  argTypes: {
    variant: {
      control: "select",
      options: ["default", "info", "success", "warning", "error"],
    },
  },
} satisfies Meta<typeof Alert>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: (args: ComponentProps<typeof Alert>) => (
    <Alert {...args} className="max-w-md">
      <InfoIcon aria-hidden="true" />
      <AlertTitle>Heads up</AlertTitle>
      <AlertDescription>You can add components to your app.</AlertDescription>
    </Alert>
  ),
};

export const AllVariants: Story = {
  render: () => (
    <div className="flex max-w-md flex-col gap-3">
      <Alert variant="info">
        <InfoIcon aria-hidden="true" />
        <AlertTitle>Info</AlertTitle>
        <AlertDescription>An informational message.</AlertDescription>
      </Alert>
      <Alert variant="success">
        <CheckCircleIcon aria-hidden="true" />
        <AlertTitle>Success</AlertTitle>
        <AlertDescription>Your changes were saved.</AlertDescription>
      </Alert>
      <Alert variant="warning">
        <WarningIcon aria-hidden="true" />
        <AlertTitle>Warning</AlertTitle>
        <AlertDescription>This action needs review.</AlertDescription>
      </Alert>
      <Alert variant="error">
        <XCircleIcon aria-hidden="true" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>Something went wrong.</AlertDescription>
      </Alert>
    </div>
  ),
};
