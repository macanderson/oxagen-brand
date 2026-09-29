// @vitest-environment jsdom
// Moved from oxagen apps/app/src/ui/attachment.test.tsx at ddb85803.
// The attachment chip, ported from shadcn's base attachment (#4690): each
// slot carries the data attribute the styles read, an uploading chip is busy,
// the line under the name keeps each fact in its own element, and the action
// is a named button that never submits the form around it.
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import {
  ATTACHMENT_ACCEPT,
  Attachment,
  AttachmentAction,
  AttachmentActions,
  AttachmentCard,
  AttachmentContent,
  AttachmentDescription,
  AttachmentGroup,
  AttachmentMedia,
  AttachmentTitle,
  attachmentKind,
  formatAttachmentSize,
} from "./attachment";

afterEach(cleanup);

function Chip({
  state,
  onSubmit = () => undefined,
}: {
  state?: "uploading" | "error" | "done";
  onSubmit?: () => void;
}) {
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit();
      }}
    >
      <AttachmentGroup>
        <Attachment state={state} size="sm" data-testid="chip">
          <AttachmentMedia>
            <svg aria-hidden="true" />
          </AttachmentMedia>
          <AttachmentContent>
            <AttachmentTitle title="report.pdf">report.pdf</AttachmentTitle>
            <AttachmentDescription data-testid="description">
              <span>PDF</span>
              <span>2.4 MB</span>
            </AttachmentDescription>
          </AttachmentContent>
          <AttachmentActions>
            <AttachmentAction aria-label="Remove report.pdf">
              <svg aria-hidden="true" />
            </AttachmentAction>
          </AttachmentActions>
        </Attachment>
      </AttachmentGroup>
    </form>
  );
}

describe("Attachment", () => {
  it("marks every slot and carries the state and size the styles read", () => {
    const { container } = render(<Chip state="error" />);
    const chip = screen.getByTestId("chip");
    expect(chip).toHaveAttribute("data-slot", "attachment");
    expect(chip).toHaveAttribute("data-state", "error");
    expect(chip).toHaveAttribute("data-size", "sm");
    for (const slot of [
      "attachment-group",
      "attachment-media",
      "attachment-content",
      "attachment-title",
      "attachment-description",
      "attachment-actions",
      "attachment-action",
    ]) {
      expect(container.querySelector(`[data-slot="${slot}"]`)).not.toBeNull();
    }
    expect(container.querySelector('[data-slot="attachment-media"]')).toHaveAttribute(
      "data-variant",
      "icon",
    );
  });

  it("is a finished file by default and busy only while it uploads", () => {
    const { rerender } = render(<Chip />);
    expect(screen.getByTestId("chip")).toHaveAttribute("data-state", "done");
    expect(screen.getByTestId("chip")).not.toHaveAttribute("aria-busy");
    rerender(<Chip state="uploading" />);
    expect(screen.getByTestId("chip")).toHaveAttribute("aria-busy", "true");
  });

  it("keeps the kind and the size in separate elements with no punctuation between them", () => {
    render(<Chip />);
    const description = screen.getByTestId("description");
    expect(Array.from(description.children, (c) => c.textContent)).toEqual([
      "PDF",
      "2.4 MB",
    ]);
    expect(description.textContent).not.toMatch(/[·,]/);
  });

  it("draws its action as a named button that does not submit the form (negative)", () => {
    const onSubmit = vi.fn();
    render(<Chip onSubmit={onSubmit} />);
    const remove = screen.getByRole("button", { name: "Remove report.pdf" });
    expect(remove).toHaveAttribute("type", "button");
    fireEvent.click(remove);
    expect(onSubmit).not.toHaveBeenCalled();
  });
});

describe("attachmentKind", () => {
  it.each([
    ["q3-incident-review.pdf", "PDF"],
    ["latency-dashboard.png", "PNG"],
    ["refund-runbook.md", "Markdown"],
    ["notes.markdown", "Markdown"],
    ["photo.jpg", "JPEG"],
    ["deploy.yml", "YAML"],
    ["Makefile", "File"],
  ])("reads %s as %s", (name, kind) => {
    expect(attachmentKind(name)).toBe(kind);
  });
});

describe("formatAttachmentSize", () => {
  it("shows one decimal place in megabytes from 1 MB up", () => {
    expect(formatAttachmentSize(2516582)).toBe("2.4 MB");
    expect(formatAttachmentSize(1048576)).toBe("1.0 MB");
  });

  it("shows whole kilobytes below 1 MB and never less than 1 KB", () => {
    expect(formatAttachmentSize(348160)).toBe("340 KB");
    expect(formatAttachmentSize(12)).toBe("1 KB");
  });
});

describe("ATTACHMENT_ACCEPT", () => {
  it("lists every kind the card has a glyph for", () => {
    expect(ATTACHMENT_ACCEPT.split(",")).toEqual(
      expect.arrayContaining([".pdf", ".png", ".md", ".yaml", ".sh"]),
    );
  });
});

describe("AttachmentCard", () => {
  it("shows the name, then the kind and the size as two elements", () => {
    const { container } = render(
      <AttachmentCard
        file={{ id: "1", name: "q3-incident-review.pdf", size: 2516582 }}
      />,
    );
    expect(screen.getByText("q3-incident-review.pdf")).toHaveAttribute(
      "data-slot",
      "attachment-title",
    );
    const description = container.querySelector(
      '[data-slot="attachment-description"]',
    );
    expect(Array.from(description?.children ?? [], (c) => c.textContent)).toEqual(
      ["PDF", "2.4 MB"],
    );
    expect(
      container.querySelector('[data-slot="attachment-media"] svg'),
    ).toHaveAttribute("aria-hidden", "true");
  });

  it("reads Uploading, is busy, and shimmers its name while it uploads", () => {
    const { container } = render(
      <AttachmentCard
        file={{ id: "1", name: "refund-runbook.md", size: 9216, state: "uploading" }}
      />,
    );
    const card = container.querySelector('[data-slot="attachment"]');
    expect(card).toHaveAttribute("aria-busy", "true");
    expect(screen.getByText("Uploading")).toBeInTheDocument();
    expect(screen.queryByText("Markdown")).toBeNull();
    expect(screen.getByText("refund-runbook.md").className).toContain(
      "group-data-[state=uploading]/attachment:text-shimmer",
    );
  });

  it("shows the preview image in the tile when the file has one", () => {
    const { container } = render(
      <AttachmentCard
        file={{
          id: "1",
          name: "latency-dashboard.png",
          size: 348160,
          previewUrl: "data:image/png;base64,iVBORw0KGgo=",
        }}
      />,
    );
    const media = container.querySelector('[data-slot="attachment-media"]');
    expect(media).toHaveAttribute("data-variant", "image");
    expect(media?.querySelector("img")).toHaveAttribute("alt", "");
  });

  it("names its remove button after the file and passes the file back", () => {
    const onRemove = vi.fn();
    const file = { id: "7", name: "latency-dashboard.png", size: 348160 };
    render(<AttachmentCard file={file} onRemove={onRemove} />);
    fireEvent.click(
      screen.getByRole("button", { name: "Remove latency-dashboard.png" }),
    );
    expect(onRemove).toHaveBeenCalledWith(file);
  });

  it("has no remove button without onRemove (negative)", () => {
    render(
      <AttachmentCard file={{ id: "1", name: "refund-runbook.md", size: 9216 }} />,
    );
    expect(screen.queryByRole("button")).toBeNull();
  });
});
