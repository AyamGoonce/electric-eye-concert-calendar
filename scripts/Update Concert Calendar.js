ObjC.import("stdlib");

const app = Application.currentApplication();
app.includeStandardAdditions = true;

const repository = "AyamGoonce/electric-eye-concert-calendar";
const workflow = "Update Electric Eye Concert Calendar";
const branch = "supersonic-scraper";
const statusUrl = "https://github.com/AyamGoonce/electric-eye-concert-calendar/actions/workflows/update-calendar.yml";

try {
  const command = [
    "/bin/zsh -lc",
    quotedForm("gh auth status --hostname github.com >/dev/null && gh workflow run " +
      quotedForm(workflow) + " --repo " + quotedForm(repository) + " --ref " + quotedForm(branch))
  ].join(" ");
  app.doShellScript(command);
  const response = app.displayDialog("Calendar update started on GitHub.", {
    withTitle: "Update Concert Calendar",
    buttons: ["OK", "Open Update Status"],
    defaultButton: "OK",
    withIcon: "note"
  });
  if (response.buttonReturned === "Open Update Status") {
    app.openLocation(statusUrl);
  }
} catch (error) {
  app.displayDialog("The calendar update could not be requested.\n\n" + error.message, {
    withTitle: "Update Concert Calendar",
    buttons: ["OK"],
    defaultButton: "OK",
    withIcon: "stop"
  });
}

function quotedForm(value) {
  return "'" + String(value).replace(/'/g, "'\\''") + "'";
}
