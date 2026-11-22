"""Regression coverage for sorted Apple identity sheets and the generated worker."""
import importlib.util
from pathlib import Path
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
CODE = ROOT / "deliverables" / "apple-related" / "Code.gs"
GENERATOR = ROOT / "tools" / "build_apple_related_deliverables.py"


class AppleSortedIdentityTests(unittest.TestCase):
    def test_generator_and_deliverable_remain_in_sync(self):
        spec = importlib.util.spec_from_file_location("apple_generation", GENERATOR)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # The full builder needs an externally generated artist-index.json,
        # which CI deliberately does not create. Compare its worker template
        # directly with the committed deliverable without invoking the export.
        template = module.WORKER
        template = template.split("function eeAssemblyIdentityRows_(", 1)[1]
        template = "function eeAssemblyIdentityRows_(" + template.split(
            "function eeSeedArtistCataloguesFromGeneration2()", 1
        )[0]
        template = template.replace(
            "function eeAssembleArticlePayloadsWorker()",
            "function eeAssembleArticlePayloadsMaintenanceWorker_()",
        )
        source = CODE.read_text(encoding="utf-8")
        delivered = source.split("function eeAssemblyIdentityRows_(", 1)[1]
        delivered = "function eeAssemblyIdentityRows_(" + delivered.split(
            "/* Old scheduled entry points", 1
        )[0]
        self.assertEqual(template.strip(), delivered.strip())

    def test_worker_does_not_use_sheet_row_as_progress_identity(self):
        source = CODE.read_text(encoding="utf-8")
        worker = source.split("function eeAssembleArticlePayloadsMaintenanceWorker_() {", 1)[1].split(
            "/* Old scheduled entry points", 1
        )[0]
        self.assertIn("EE_APPLE_ASSEMBLY_AFTER_POST_ID", source)
        self.assertIn("identityRows=eeAssemblyIdentityRows_(values)", worker)
        self.assertIn("identityRow=identityRows[row].values", worker)
        self.assertNotIn("JSON.parse(String(values[row][4]", worker)
        self.assertIn("eeAdvanceAssemblyCursor_", worker)
        self.assertIn("for(var row=cursor;row<identityRows.length", worker)
        self.assertIn("for(var row=0;row<values.length;row+=1)if(String(values[row][key])", source)

    @unittest.skipUnless(shutil.which("node"), "Runtime JS checks run in CI; Node not installed locally")
    def test_sorted_headers_malformed_rows_and_cursor_resume(self):
        script = r"""
const fs=require("fs"),assert=require("assert");
const source=fs.readFileSync(process.argv[1],"utf8");
const snippet=source.slice(source.indexOf("function eeAssemblyIdentityRows_("),
                           source.indexOf("var EE_APPLE_ASSEMBLY_ROW_LIMIT=25;"));
const logs=[];global.console={log:x=>logs.push(x)};
eval(snippet);
const a=["200","https://example/a","2026-11-01","2",'["a"]','["A"]'];
const b=["100","https://example/b","2026-11-02","2",'["b"]','["B"]'];
const heading=["postId","canonicalUrl","analyzedAt","analysisVersion",
               "primaryArtistKeys","primaryArtists","confidence","ambiguous","evidenceJson","articleType"];
const broken=["300","https://example/c","2026-11-03","2","broken",'["C"]'];
const rows=eeAssemblyIdentityRows_([a,heading,b,broken]);
assert.deepStrictEqual(rows.map(x=>x.postId),["100","200"]);
assert.strictEqual(eeAssemblyResumeIndex_(rows,""),0);
assert.strictEqual(eeAssemblyResumeIndex_(rows,"100"),1);
assert.strictEqual(eeAssemblyResumeIndex_(rows,"200"),2);
assert.deepStrictEqual(eeAssemblyIdentityRows_([broken,b,a,heading]).map(x=>x.postId),["100","200"]);
const props={v:{},setProperty(k,v){this.v[k]=v;}};
eeAdvanceAssemblyCursor_(props,"100",1);
assert.strictEqual(props.v.EE_APPLE_ASSEMBLY_AFTER_POST_ID,"100");
assert.strictEqual(props.v.EE_APPLE_ASSEMBLY_INDEX,"1");
assert(logs.some(x=>x.includes("APPLE_IDENTITY_SHEET_AUDIT")));
"""
        result = subprocess.run(
            ["node", "-e", script, str(CODE)], capture_output=True, text=True,
            cwd=ROOT, timeout=20, check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)


if __name__ == "__main__":
    unittest.main()
