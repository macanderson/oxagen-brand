// @vitest-environment jsdom
// The composer with attachments (#246): files arrive through the attach
// button, paste, and drop, each reaches `onFilesAdd`, a card's remove button
// reaches `onFileRemove`, Send waits for every upload, and the sent turn shows
// its cards with no remove button.
import {
  cleanup,
  createEvent,
  fireEvent,
  render,
  screen,
} from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { expectNoAxe } from "../test/expect-no-axe";
import { ATTACHMENT_ACCEPT, type AttachmentFile } from "./attachment";
import { Composer, ComposerSentTurn } from "./composer";

afterEach(cleanup);

const PDF: AttachmentFile = {
  id: "f1",
  name: "q3-incident-review.pdf",
  size: 2516582,
};
const PNG: AttachmentFile = {
  id: "f2",
  name: "latency-dashboard.png",
  size: 348160,
};
const MD_UPLOADING: AttachmentFile = {
  id: "f3",
  name: "refund-runbook.md",
  size: 9216,
  state: "uploading",
};

function aFile(name = "notes.md") {
  return new File(["# Notes"], name, { type: "text/markdown" });
}

function composerRoot(container: HTMLElement): HTMLElement {
  const root = container.querySelector<HTMLElement>('[data-slot="composer"]');
  if (!root) throw new Error("composer root not rendered");
  return root;
}

function fileInput(container: HTMLElement): HTMLInputElement {
  const input = container.querySelector<HTMLInputElement>(
    '[data-slot="composer-file-input"]',
  );
  if (!input) throw new Error("file input not rendered");
  return input;
}

describe("Composer input", () => {
  it("names the input and shows the placeholder", () => {
    render(<Composer />);
    const input = screen.getByRole("textbox", { name: "Ask Stella" });
    expect(input).toHaveAttribute("placeholder", "Ask about this workspace");
  });

  it("sends the text on Enter and clears it", () => {
    const onSend = vi.fn();
    render(<Composer onSend={onSend} />);
    const input = screen.getByRole("textbox", { name: "Ask Stella" });
    fireEvent.change(input, { target: { value: "Why did the run fail?" } });
    fireEvent.keyDown(input, { key: "Enter" });
    expect(onSend).toHaveBeenCalledWith("Why did the run fail?");
    expect(input).toHaveValue("");
  });

  it("keeps a new line on Shift+Enter", () => {
    const onSend = vi.fn();
    render(<Composer defaultValue="First line" onSend={onSend} />);
    const input = screen.getByRole("textbox", { name: "Ask Stella" });
    fireEvent.keyDown(input, { key: "Enter", shiftKey: true });
    expect(onSend).not.toHaveBeenCalled();
  });

  it("disables Send with no text and no files", () => {
    render(<Composer />);
    expect(screen.getByRole("button", { name: "Send" })).toBeDisabled();
  });

  it("sends from the Send button", () => {
    const onSend = vi.fn();
    render(<Composer value="Summarise the run" onSend={onSend} />);
    fireEvent.click(screen.getByRole("button", { name: "Send" }));
    expect(onSend).toHaveBeenCalledWith("Summarise the run");
  });
});

describe("Composer attach button", () => {
  it("opens the file picker", () => {
    const { container } = render(<Composer />);
    const input = fileInput(container);
    const click = vi.spyOn(input, "click").mockImplementation(() => {});
    fireEvent.click(screen.getByRole("button", { name: "Attach files" }));
    expect(click).toHaveBeenCalledTimes(1);
  });

  it("offers several files of the kinds the kit knows", () => {
    const { container } = render(<Composer />);
    const input = fileInput(container);
    expect(input).toHaveAttribute("type", "file");
    expect(input.multiple).toBe(true);
    expect(input).toHaveAttribute("accept", ATTACHMENT_ACCEPT);
  });

  it("hands the picked files to onFilesAdd", () => {
    const onFilesAdd = vi.fn();
    const { container } = render(<Composer onFilesAdd={onFilesAdd} />);
    const picked = [aFile("a.md"), aFile("b.md")];
    fireEvent.change(fileInput(container), { target: { files: picked } });
    expect(onFilesAdd).toHaveBeenCalledWith(picked);
  });
});

describe("Composer paste", () => {
  it("hands pasted files to onFilesAdd", () => {
    const onFilesAdd = vi.fn();
    render(<Composer onFilesAdd={onFilesAdd} />);
    const file = aFile();
    fireEvent.paste(screen.getByRole("textbox", { name: "Ask Stella" }), {
      clipboardData: { files: [file] },
    });
    expect(onFilesAdd).toHaveBeenCalledWith([file]);
  });

  it("leaves a text paste alone", () => {
    const onFilesAdd = vi.fn();
    render(<Composer onFilesAdd={onFilesAdd} />);
    fireEvent.paste(screen.getByRole("textbox", { name: "Ask Stella" }), {
      clipboardData: { files: [] },
    });
    expect(onFilesAdd).not.toHaveBeenCalled();
  });
});

describe("Composer drop", () => {
  it("shows the drop target while files are dragged over it", () => {
    const { container } = render(<Composer />);
    const root = composerRoot(container);
    expect(root).not.toHaveAttribute("data-dragging");
    fireEvent.dragEnter(root, {
      dataTransfer: { types: ["Files"], files: [] },
    });
    expect(root).toHaveAttribute("data-dragging");
  });

  it("ignores a drag that carries no files", () => {
    const { container } = render(<Composer />);
    const root = composerRoot(container);
    fireEvent.dragEnter(root, {
      dataTransfer: { types: ["text/plain"], files: [] },
    });
    expect(root).not.toHaveAttribute("data-dragging");
  });

  it("keeps the drop target while the pointer moves onto a child", () => {
    const { container } = render(<Composer />);
    const root = composerRoot(container);
    fireEvent.dragEnter(root, {
      dataTransfer: { types: ["Files"], files: [] },
    });
    const leave = createEvent.dragLeave(root);
    Object.defineProperty(leave, "relatedTarget", {
      value: screen.getByRole("textbox", { name: "Ask Stella" }),
    });
    fireEvent(root, leave);
    expect(root).toHaveAttribute("data-dragging");
  });

  it("clears the drop target when the pointer leaves", () => {
    const { container } = render(<Composer />);
    const root = composerRoot(container);
    fireEvent.dragEnter(root, {
      dataTransfer: { types: ["Files"], files: [] },
    });
    const leave = createEvent.dragLeave(root);
    Object.defineProperty(leave, "relatedTarget", { value: document.body });
    fireEvent(root, leave);
    expect(root).not.toHaveAttribute("data-dragging");
  });

  it("hands dropped files to onFilesAdd and clears the drop target", () => {
    const onFilesAdd = vi.fn();
    const { container } = render(<Composer onFilesAdd={onFilesAdd} />);
    const root = composerRoot(container);
    const file = aFile();
    fireEvent.dragEnter(root, {
      dataTransfer: { types: ["Files"], files: [] },
    });
    fireEvent.drop(root, {
      dataTransfer: { types: ["Files"], files: [file] },
    });
    expect(onFilesAdd).toHaveBeenCalledWith([file]);
    expect(root).not.toHaveAttribute("data-dragging");
  });

  it("shows the drop target when dropActive is set", () => {
    const { container } = render(<Composer dropActive />);
    expect(composerRoot(container)).toHaveAttribute("data-dragging");
  });

  it("takes no files while disabled", () => {
    const onFilesAdd = vi.fn();
    const { container } = render(<Composer disabled onFilesAdd={onFilesAdd} />);
    fireEvent.drop(composerRoot(container), {
      dataTransfer: { types: ["Files"], files: [aFile()] },
    });
    expect(onFilesAdd).not.toHaveBeenCalled();
  });
});

describe("Composer files", () => {
  it("shows a card for each file", () => {
    render(<Composer files={[PDF, PNG]} />);
    const group = screen.getByRole("group", { name: "Attached files" });
    expect(group).toHaveTextContent("q3-incident-review.pdf");
    expect(group).toHaveTextContent("latency-dashboard.png");
  });

  it("hands the removed file to onFileRemove", () => {
    const onFileRemove = vi.fn();
    render(<Composer files={[PDF, PNG]} onFileRemove={onFileRemove} />);
    fireEvent.click(
      screen.getByRole("button", { name: "Remove latency-dashboard.png" }),
    );
    expect(onFileRemove).toHaveBeenCalledWith(PNG);
  });

  it("sends files with no text", () => {
    const onSend = vi.fn();
    render(<Composer files={[PDF]} onSend={onSend} />);
    fireEvent.click(screen.getByRole("button", { name: "Send" }));
    expect(onSend).toHaveBeenCalledWith("");
  });

  it("holds Send while a file uploads", () => {
    const onSend = vi.fn();
    render(
      <Composer
        files={[PDF, MD_UPLOADING]}
        value="Compare these"
        onSend={onSend}
      />,
    );
    expect(screen.getByRole("button", { name: "Send" })).toBeDisabled();
    fireEvent.keyDown(screen.getByRole("textbox", { name: "Ask Stella" }), {
      key: "Enter",
    });
    expect(onSend).not.toHaveBeenCalled();
  });
});

describe("ComposerSentTurn", () => {
  it("shows the cards with no remove button, then the text", () => {
    const { container } = render(
      <ComposerSentTurn files={[PDF, PNG]}>
        What changed in the refund path?
      </ComposerSentTurn>,
    );
    expect(container).toHaveTextContent("q3-incident-review.pdf");
    expect(screen.queryByRole("button")).toBeNull();
    expect(container.querySelector("p")).toHaveTextContent(
      "What changed in the refund path?",
    );
  });
});

describe("Composer accessibility", () => {
  it("has no axe violations when empty", async () => {
    const { container } = render(<Composer />);
    await expectNoAxe(container);
  });

  it("has no axe violations with files, one uploading", async () => {
    const { container } = render(
      <Composer files={[PDF, PNG, MD_UPLOADING]} onFileRemove={() => {}} />,
    );
    await expectNoAxe(container);
  });

  it("has no axe violations on the drop target", async () => {
    const { container } = render(<Composer dropActive />);
    await expectNoAxe(container);
  });

  it("has no axe violations on a sent turn", async () => {
    const { container } = render(
      <ComposerSentTurn files={[PDF]}>Summarise this review.</ComposerSentTurn>,
    );
    await expectNoAxe(container);
  });
});
