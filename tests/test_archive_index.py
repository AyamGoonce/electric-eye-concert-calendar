import json
import shutil
import subprocess
import unittest
from pathlib import Path


ARCHIVE_INDEX = (
    Path(__file__).resolve().parents[1]
    / "concert_calendar"
    / "static"
    / "archive-index.js"
)


class ArchiveIndexSearchTests(unittest.TestCase):
    def test_production_search_uses_only_explicit_routing_fields(self):
        source = ARCHIVE_INDEX.read_text(encoding="utf-8")

        self.assertNotIn("relationshipFields", source)
        self.assertNotIn("relatedSlugsBySlug", source)
        self.assertIn("identity.searchAssociations", source)
        self.assertIn("identity.searchLinks", source)
        self.assertIn("(artist.ar || []).forEach", source)

    def test_production_genre_visibility_uses_one_qualifying_artist(self):
        source = ARCHIVE_INDEX.read_text(encoding="utf-8")

        self.assertIn("item.artistCount >= 1", source)
        self.assertNotIn("item.artistCount >= 2", source)
        self.assertIn("children[item.name].some(shouldKeep)", source)

    def test_relationship_metadata_does_not_expand_global_artist_search(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js is unavailable")

        runner = r'''
const fs = require("node:fs");
const vm = require("node:vm");
let source = fs.readFileSync(process.argv[1], "utf8");
source = source.replace(
  /\}\(\)\);\s*$/,
  "globalThis.__archiveTest={makeArtistItems:makeArtistItems};}());"
);
const articles = [
  {t:"Jazz à la Villette shared feature",u:"https://example.test/jazz",d:"2022-09-04",a:["scary-goldings","john-scofield","mononeon","louis-cole"]},
  {t:"Sparks feature",u:"https://example.test/sparks",d:"2026-01-01",a:["sparks"]},
  {t:"Public Image Ltd. feature",u:"https://example.test/pil",d:"2026-01-02",a:["public-image-ltd"]}
];
function artist(name, articleId, identity) {
  return {n:name,al:[],ar:[articleId],da:[articleId],identity:Object.assign({hideFromArtistIndex:false},identity||{})};
}
const artists = {
  "louis-cole":artist("Louis Cole",0,{collaborators:["MonoNeon"]}),
  "mononeon":artist("MonoNeon",0,{collaborators:["Louis Cole","Scary Goldings"]}),
  "scary-goldings":artist("Scary Goldings",0,{collaborators:["John Scofield","MonoNeon"]}),
  "john-scofield":artist("John Scofield",0,{collaborators:["Scary Goldings"]}),
  "sparks":artist("Sparks",1,{members:["Ron Mael"]}),
  "public-image-ltd":artist("Public Image Ltd.",2,{members:["John Lydon"]})
};
const terms = {};
Object.keys(artists).forEach((slug) => { terms[artists[slug].n] = slug; });
const sandbox = {
  window:{
    ElectricEyeArtistLookup:{terms:terms},
    ElectricEyeContentIndex:{artists:artists,articles:articles,relationshipNodes:{
      "ron-mael":{n:"Ron Mael",al:[],identity:{searchLinks:["Sparks"]}},
      "john-lydon":{n:"John Lydon",al:["Johnny Rotten"],identity:{searchAssociations:["Public Image Ltd."]}}
    }}
  },
  document:{readyState:"loading",addEventListener:function(){}},
  console:console
};
vm.createContext(sandbox);
vm.runInContext(source,sandbox);
const items = sandbox.__archiveTest.makeArtistItems();
function normalize(value) { return (value||"").toLowerCase(); }
function matches(query) {
  query=normalize(query);
  return items.filter((item) => [item.name].concat(item.searchTerms||[]).some((value) => normalize(value).includes(query))).map((item) => item.name);
}
process.stdout.write(JSON.stringify({
  louis:matches("Louis Cole"),
  scary:matches("Scary Goldings"),
  ron:matches("Ron Mael"),
  rotten:matches("Johnny Rotten")
}));
'''
        result = subprocess.run(
            [node, "-e", runner, str(ARCHIVE_INDEX)],
            check=True,
            capture_output=True,
            text=True,
        )
        matches = json.loads(result.stdout)

        self.assertEqual(["Louis Cole"], matches["louis"])
        self.assertEqual(["Scary Goldings"], matches["scary"])
        self.assertEqual(["Sparks"], matches["ron"])
        self.assertEqual(["Public Image Ltd."], matches["rotten"])
