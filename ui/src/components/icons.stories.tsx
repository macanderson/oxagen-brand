import type { Meta, StoryObj } from "@storybook/react-vite";
import {
  ArrowCounterClockwiseIcon,
  ArrowSquareOutIcon,
  AtIcon,
  BellIcon,
  BirdIcon,
  BookIcon,
  BrainIcon,
  BugIcon,
  BuildingOfficeIcon,
  CaretDownIcon,
  CaretLeftIcon,
  CaretRightIcon,
  CellTowerIcon,
  ChartBarIcon,
  ChatIcon,
  CheckCircleIcon,
  CheckIcon,
  CompassIcon,
  CopyIcon,
  CreditCardIcon,
  CurrencyDollarIcon,
  DeviceMobileIcon,
  DotsThreeIcon,
  DownloadSimpleIcon,
  EnvelopeSimpleIcon,
  FileCodeIcon,
  FileIcon,
  FileImageIcon,
  FilePdfIcon,
  FileTextIcon,
  FlaskIcon,
  FolderIcon,
  GearIcon,
  GearSixIcon,
  GitBranchIcon,
  GitCommitIcon,
  GitPullRequestIcon,
  GraphIcon,
  HardDrivesIcon,
  InfoIcon,
  KeyIcon,
  ListChecksIcon,
  LockIcon,
  MagicWandIcon,
  MagnifyingGlassIcon,
  MicroscopeIcon,
  MoonIcon,
  PackageIcon,
  PaperPlaneTiltIcon,
  PaperclipIcon,
  PauseIcon,
  PencilLineIcon,
  PlanetIcon,
  PlantIcon,
  PlayIcon,
  PlusIcon,
  PowerIcon,
  ReceiptIcon,
  RobotIcon,
  RocketLaunchIcon,
  ShieldCheckIcon,
  ShieldIcon,
  SkipBackIcon,
  SkipForwardIcon,
  SlackLogoIcon,
  SparkleIcon,
  SteeringWheelIcon,
  StethoscopeIcon,
  StopIcon,
  SunIcon,
  TagIcon,
  TargetIcon,
  TerminalWindowIcon,
  ThumbsDownIcon,
  ThumbsUpIcon,
  TrashIcon,
  TreeViewIcon,
  UploadSimpleIcon,
  UserIcon,
  WallIcon,
  WarningIcon,
  WrenchIcon,
  XCircleIcon,
  XIcon,
  type Icon,
} from "@phosphor-icons/react";

/**
 * The Phosphor icons the kit uses, under the names it imports them by.
 */
const meta = {
  title: "Foundations/Icons",
  parameters: { layout: "padded" },
} satisfies Meta;
export default meta;
type Story = StoryObj<typeof meta>;

interface IconRow {
  /** The icon's key in the v3 mockup. */
  key: string;
  /** The mockup map that holds the key. */
  map: string;
  /** The mockup file under `mockups/src/`. */
  file: string;
  /** The Phosphor icon name, its file name under `assets/regular/`. */
  name: string;
  icon: Icon;
  /** The key a row reads its drawing from, when it borrows one. */
  through?: string;
}

function row(
  key: string,
  map: string,
  file: string,
  name: string,
  icon: Icon,
  through?: string,
): IconRow {
  return { key, map, file, name, icon, through };
}

/**
 * The v3 mockup's icon map, from `design/icons.md` in oxagen-roadmap. The
 * brand marks, harness and tracker logos, and the QR code are drawings, not
 * icons, so they are not in this map.
 */
const ICON_MAP: IconRow[] = [
  row("work", "NAV_GLYPH", "marks.js", "list-checks", ListChecksIcon),
  row("agents", "NAV_GLYPH", "marks.js", "robot", RobotIcon),
  row("steering", "NAV_GLYPH", "marks.js", "steering-wheel", SteeringWheelIcon),
  row("spend", "NAV_GLYPH", "marks.js", "currency-dollar", CurrencyDollarIcon),
  row("tools", "NAV_GLYPH", "marks.js", "wrench", WrenchIcon),
  row("search", "NAV_GLYPH", "marks.js", "magnifying-glass", MagnifyingGlassIcon),
  row("bell", "NAV_GLYPH", "marks.js", "bell", BellIcon),
  row("user", "NAV_GLYPH", "marks.js", "user", UserIcon),
  row("org", "NAV_GLYPH", "marks.js", "building-office", BuildingOfficeIcon),
  row("repo", "NAV_GLYPH", "marks.js", "book", BookIcon),
  row("git", "NAV_GLYPH", "marks.js", "git-branch", GitBranchIcon),
  row("lock", "NAV_GLYPH", "marks.js", "lock", LockIcon),
  row("shield", "NAV_GLYPH", "marks.js", "shield", ShieldIcon),
  row("runtimes", "NAV_GLYPH", "marks.js", "hard-drives", HardDrivesIcon),
  row("dir", "NAV_GLYPH", "marks.js", "folder", FolderIcon),
  row("billing", "NAV_GLYPH", "marks.js", "credit-card", CreditCardIcon),
  row("audit", "NAV_GLYPH", "marks.js", "shield-check", ShieldCheckIcon),
  row("more", "NAV_GLYPH", "marks.js", "dots-three", DotsThreeIcon),
  row("rocket", "AV_ICONS", "marks.js", "rocket-launch", RocketLaunchIcon),
  row("compass", "AV_ICONS", "marks.js", "compass", CompassIcon),
  row("microscope", "AV_ICONS", "marks.js", "microscope", MicroscopeIcon),
  row("stethoscope", "AV_ICONS", "marks.js", "stethoscope", StethoscopeIcon),
  row("pencil-line", "AV_ICONS", "marks.js", "pencil-line", PencilLineIcon),
  row("receipt", "AV_ICONS", "marks.js", "receipt", ReceiptIcon),
  row("wrench", "AV_ICONS", "marks.js", "wrench", WrenchIcon),
  row("flask-conical", "AV_ICONS", "marks.js", "flask", FlaskIcon),
  row("key-round", "AV_ICONS", "marks.js", "key", KeyIcon),
  row("package", "AV_ICONS", "marks.js", "package", PackageIcon),
  row("satellite", "AV_ICONS", "marks.js", "planet", PlanetIcon),
  row("bot", "AV_ICONS", "marks.js", "robot", RobotIcon),
  row("bird", "AV_ICONS", "marks.js", "bird", BirdIcon),
  row("bug", "AV_ICONS", "marks.js", "bug", BugIcon),
  row("sprout", "AV_ICONS", "marks.js", "plant", PlantIcon),
  row("cog", "AV_ICONS", "marks.js", "gear-six", GearSixIcon),
  row("brain", "AV_ICONS", "marks.js", "brain", BrainIcon),
  row("search", "AV_ICONS", "marks.js", "magnifying-glass", MagnifyingGlassIcon),
  row("radio-tower", "AV_ICONS", "marks.js", "cell-tower", CellTowerIcon),
  row("wand-sparkles", "AV_ICONS", "marks.js", "magic-wand", MagicWandIcon),
  row("brick-wall", "AV_ICONS", "marks.js", "wall", WallIcon),
  row("target", "AV_ICONS", "marks.js", "target", TargetIcon),
  row("folder-tree", "AV_ICONS", "marks.js", "tree-view", TreeViewIcon),
  row("git-branch", "AV_ICONS", "marks.js", "git-branch", GitBranchIcon),
  row(
    "git-pull-request",
    "AV_ICONS",
    "marks.js",
    "git-pull-request",
    GitPullRequestIcon,
  ),
  row("shield-check", "AV_ICONS", "marks.js", "shield-check", ShieldCheckIcon),
  row("sessions", "GLYPH", "core.js", "terminal-window", TerminalWindowIcon),
  row("servers", "GLYPH", "core.js", "hard-drives", HardDrivesIcon),
  row("play", "GLYPH", "core.js", "play", PlayIcon),
  row("pause", "GLYPH", "core.js", "pause", PauseIcon),
  row(
    "restart",
    "GLYPH",
    "core.js",
    "arrow-counter-clockwise",
    ArrowCounterClockwiseIcon,
  ),
  row("prev", "GLYPH", "core.js", "skip-back", SkipBackIcon),
  row("next", "GLYPH", "core.js", "skip-forward", SkipForwardIcon),
  row("x", "GLYPH", "core.js", "x", XIcon),
  row("check", "GLYPH", "core.js", "check", CheckIcon),
  row("plus", "GLYPH", "core.js", "plus", PlusIcon),
  row("down", "GLYPH", "core.js", "caret-down", CaretDownIcon),
  row("right", "GLYPH", "core.js", "caret-right", CaretRightIcon),
  row("copy", "GLYPH", "core.js", "copy", CopyIcon),
  row("import", "GLYPH", "core.js", "download-simple", DownloadSimpleIcon),
  row("send", "GLYPH", "core.js", "paper-plane-tilt", PaperPlaneTiltIcon),
  row("key", "GLYPH", "core.js", "key", KeyIcon),
  row("moon", "GLYPH", "core.js", "moon", MoonIcon),
  row("sun", "GLYPH", "core.js", "sun", SunIcon),
  row("phone", "GLYPH", "core.js", "device-mobile", DeviceMobileIcon),
  row("stop", "GLYPH", "core.js", "stop", StopIcon),
  row("file", "GLYPH", "core.js", "file", FileIcon),
  row("tag", "GLYPH", "core.js", "tag", TagIcon),
  row("spark", "GLYPH", "core.js", "sparkle", SparkleIcon),
  row("ext", "GLYPH", "core.js", "arrow-square-out", ArrowSquareOutIcon),
  row("circle-check", "GLYPH", "core.js", "check-circle", CheckCircleIcon),
  row("info", "GLYPH", "core.js", "info", InfoIcon),
  row("warning", "GLYPH", "core.js", "warning", WarningIcon),
  row("circle-x", "GLYPH", "core.js", "x-circle", XCircleIcon),
  row("paperclip", "GLYPH", "core.js", "paperclip", PaperclipIcon),
  row("file-pdf", "GLYPH", "core.js", "file-pdf", FilePdfIcon),
  row("file-image", "GLYPH", "core.js", "file-image", FileImageIcon),
  row("file-text", "GLYPH", "core.js", "file-text", FileTextIcon),
  row("file-code", "GLYPH", "core.js", "file-code", FileCodeIcon),
  row("caret-left", "GLYPH", "core.js", "caret-left", CaretLeftIcon),
  row("caret-right", "GLYPH", "core.js", "caret-right", CaretRightIcon),
  row("settings", "GLYPH", "core.js", "gear", GearIcon),
  row("graph", "GLYPH", "core.js", "graph", GraphIcon),
  row("upload", "GLYPH", "core.js", "upload-simple", UploadSimpleIcon),
  row("trash", "GLYPH", "core.js", "trash", TrashIcon),
  row("power", "GLYPH", "core.js", "power", PowerIcon),
  row("mail", "GLYPH", "core.js", "envelope-simple", EnvelopeSimpleIcon),
  row("slack", "GLYPH", "core.js", "slack-logo", SlackLogoIcon),
  row("work", "GLYPH", "core.js", "list-checks", ListChecksIcon, "NAV_GLYPH.work"),
  row("agents", "GLYPH", "core.js", "robot", RobotIcon, "NAV_GLYPH.agents"),
  row(
    "steering",
    "GLYPH",
    "core.js",
    "steering-wheel",
    SteeringWheelIcon,
    "NAV_GLYPH.steering",
  ),
  row(
    "spend",
    "GLYPH",
    "core.js",
    "currency-dollar",
    CurrencyDollarIcon,
    "NAV_GLYPH.spend",
  ),
  row("lock", "GLYPH", "core.js", "lock", LockIcon, "NAV_GLYPH.lock"),
  row(
    "pr",
    "GLYPH",
    "core.js",
    "git-pull-request",
    GitPullRequestIcon,
    "AV_ICONS.git-pull-request",
  ),
  row("branch", "GLYPH", "core.js", "git-branch", GitBranchIcon, "NAV_GLYPH.git"),
  row(
    "edit",
    "GLYPH",
    "core.js",
    "pencil-line",
    PencilLineIcon,
    "AV_ICONS.pencil-line",
  ),
  row(
    "runs",
    "GLYPH",
    "core.js",
    "terminal-window",
    TerminalWindowIcon,
    "GLYPH.sessions",
  ),
  row("tools", "GLYPH", "core.js", "wrench", WrenchIcon, "NAV_GLYPH.tools"),
  row(
    "org",
    "GLYPH",
    "core.js",
    "building-office",
    BuildingOfficeIcon,
    "NAV_GLYPH.org",
  ),
  row("user", "GLYPH", "core.js", "user", UserIcon, "NAV_GLYPH.user"),
  row("bell", "GLYPH", "core.js", "bell", BellIcon, "NAV_GLYPH.bell"),
  row("shield", "GLYPH", "core.js", "shield", ShieldIcon, "NAV_GLYPH.shield"),
  row(
    "billing",
    "GLYPH",
    "core.js",
    "credit-card",
    CreditCardIcon,
    "NAV_GLYPH.billing",
  ),
  row(
    "audit",
    "GLYPH",
    "core.js",
    "shield-check",
    ShieldCheckIcon,
    "NAV_GLYPH.audit",
  ),
  row(
    "runtimes",
    "GLYPH",
    "core.js",
    "hard-drives",
    HardDrivesIcon,
    "NAV_GLYPH.runtimes",
  ),
  row(
    "search",
    "GLYPH",
    "core.js",
    "magnifying-glass",
    MagnifyingGlassIcon,
    "NAV_GLYPH.search",
  ),
  row("more", "GLYPH", "core.js", "dots-three", DotsThreeIcon, "NAV_GLYPH.more"),
  row("repo", "GLYPH", "core.js", "book", BookIcon, "NAV_GLYPH.repo"),
  row("dir", "GLYPH", "core.js", "folder", FolderIcon, "NAV_GLYPH.dir"),
  row("search", "GLYPH", "views.js", "magnifying-glass", MagnifyingGlassIcon),
  row("talk", "GLYPH", "discussions.js", "chat", ChatIcon, "DZ_GLYPH.talk"),
  row("at", "GLYPH", "discussions.js", "at", AtIcon, "DZ_GLYPH.at"),
  row("up", "STL_GLYPH", "stella.js", "thumbs-up", ThumbsUpIcon),
  row("down", "STL_GLYPH", "stella.js", "thumbs-down", ThumbsDownIcon),
  row("clip", "STL_GLYPH", "stella.js", "paperclip", PaperclipIcon),
  row("back", "STL_GLYPH", "stella.js", "caret-left", CaretLeftIcon),
  row("chart", "STL_GLYPH", "stella.js", "chart-bar", ChartBarIcon),
  row("talk", "DZ_GLYPH", "discussions.js", "chat", ChatIcon),
  row("at", "DZ_GLYPH", "discussions.js", "at", AtIcon),
  row("commit", "DZ_GLYPH", "discussions.js", "git-commit", GitCommitIcon),
  row("select chevron", "background-image", "shared.css", "caret-down", CaretDownIcon),
];

/** `paper-plane-tilt` becomes `PaperPlaneTiltIcon`, the name to import. */
function componentName(name: string): string {
  const pascal = name
    .split("-")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join("");
  return `${pascal}Icon`;
}

const HEAD = "px-3 py-2 text-left text-xs font-medium text-muted-foreground";
const CELL = "px-3 py-2 align-middle";

function IconMap() {
  return (
    <div className="flex max-w-[960px] flex-col gap-3">
      <p className="max-w-[640px] text-sm text-muted-foreground">
        Every icon the v3 mockup draws, with the Phosphor icon that replaces
        it. Import the component from <code>@phosphor-icons/react</code>, or
        from <code>@phosphor-icons/react/ssr</code> in a file with no{" "}
        <code>&quot;use client&quot;</code>. The kit draws the regular weight.
      </p>
      <div className="overflow-x-auto rounded-xl border border-border">
        <table className="w-full min-w-[640px] border-collapse text-sm">
          <caption className="sr-only">Mockup icons and their Phosphor names</caption>
          <thead className="bg-card">
            <tr className="border-b border-border">
              <th scope="col" className={HEAD}>
                Mockup key
              </th>
              <th scope="col" className={HEAD}>
                Map
              </th>
              <th scope="col" className={HEAD}>
                Icon
              </th>
              <th scope="col" className={HEAD}>
                Phosphor name
              </th>
              <th scope="col" className={HEAD}>
                Component
              </th>
            </tr>
          </thead>
          <tbody>
            {ICON_MAP.map(({ key, map, file, name, icon: Glyph, through }, index) => (
              <tr
                key={`${index}-${key}`}
                className="border-b border-border last:border-b-0 hover:bg-hl"
              >
                <td className={CELL}>
                  <code className="text-xs text-foreground">{key}</code>
                </td>
                <td className={CELL}>
                  <div className="flex flex-col">
                    <code className="text-xs text-foreground">{map}</code>
                    <span className="text-xs text-dim">{file}</span>
                    {through && (
                      <span className="text-xs text-dim">
                        Reads <code>{through}</code>
                      </span>
                    )}
                  </div>
                </td>
                <td className={CELL}>
                  <Glyph aria-hidden="true" className="size-5 text-foreground" />
                </td>
                <td className={CELL}>
                  <code className="text-xs text-foreground">{name}</code>
                </td>
                <td className={CELL}>
                  <code className="text-xs text-muted-foreground">
                    {componentName(name)}
                  </code>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// Named IconMapStory so the export does not shadow the global Map.
export const IconMapStory: Story = {
  name: "Icon map",
  render: () => <IconMap />,
};
