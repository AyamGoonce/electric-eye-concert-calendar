import json
import shutil
import subprocess
import unittest
from pathlib import Path


ARCHIVE_INDEX = Path(__file__).resolve().parents[1] / "concert_calendar" / "static" / "archive-index.js"


class ArchiveIndexSearchTests(unittest.TestCase):
    def test_production_search_separates_structural_and_collaborator_fields(self):
        source = ARCHIVE_INDEX.read_text(encoding="utf-8")
        structural_block = source.split(
            "var structuralRelationshipFields = [", 1
        )[1].split("];", 1)[0]

        for field in ("members", "formerMembers", "associatedActs", "sideProjects"):
            self.assertIn(f'"{field}"', structural_block)
        self.assertNotIn('"collaborators"', structural_block)
        self.assertIn("identity.searchAssociations", source)
        self.assertIn("identity.searchLinks", source)
        self.assertIn("(artist.ar || []).forEach", source)
        self.assertNotIn("addSearchTerm(slug, term)", source)

    def test_production_genre_visibility_uses_one_qualifying_artist(self):
        source = ARCHIVE_INDEX.read_text(encoding="utf-8")

        self.assertIn("item.artistCount >= 1", source)
        self.assertNotIn("item.artistCount >= 2", source)
        self.assertIn("children[item.name].some(shouldKeep)", source)

    def test_reviewed_relationship_graph_routes_systemically(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js is unavailable")

        runner = r'''
const fs = require("node:fs");
const vm = require("node:vm");
let source = fs.readFileSync(process.argv[1], "utf8");
source = source.replace(/\}\(\)\);\s*$/, "globalThis.__archiveTest={makeArtistItems:makeArtistItems,filterItemsForQuery:filterItemsForQuery};}());");
const articles = Array.from({length:40},(_,id)=>({t:"Article "+id,u:"https://example.test/"+id,d:"2026-01-01",pi:String(id),a:[]}));
articles[0]={t:"Jazz à la Villette shared feature",u:"https://example.test/jazz",d:"2022-09-04",pi:"jazz",a:["scary-goldings","john-scofield","mononeon","louis-cole"]};
articles[28]={t:"Iggy Pop review",u:"https://example.test/iggy",d:"2016-05-15",pi:"iggy-post",a:["iggy-pop"]};
function artist(name, articleId, identity, visible, aliases) {
  return {n:name,al:aliases||[],ar:[articleId],da:visible===false?[]:[articleId],identity:Object.assign({hideFromArtistIndex:false},identity||{})};
}
const artists = {
  "louis-cole":artist("Louis Cole",0,{collaborators:["MonoNeon"],articleSearchTerms:["MonoNeon & Louis Cole"]}),
  "mononeon":artist("MonoNeon",0,{collaborators:["Louis Cole","Scary Goldings"],articleSearchTerms:["MonoNeon & Louis Cole"]}),
  "scary-goldings":artist("Scary Goldings",0,{collaborators:["John Scofield","MonoNeon"],articleSearchTerms:["Scary Goldings feat. John Scofield"]}),
  "john-scofield":artist("John Scofield",0,{collaborators:["Scary Goldings"],articleSearchTerms:["Scary Goldings feat. John Scofield"]}),
  "sparks":artist("Sparks",1,{members:["Ron Mael","Russell Mael"]}),
  "public-image-ltd":artist("Public Image Ltd.",2,{members:["John Lydon"],formerMembers:["John McGeoch"]}),
  "the-rolling-stones":artist("The Rolling Stones",3,{members:["Ronnie Wood","Mick Jagger"]}),
  "mick-jagger":artist("Mick Jagger",4,{associatedActs:["The Rolling Stones"]},false),
  "black-sabbath":artist("Black Sabbath",5,{members:["Geezer Butler"]}),
  "ac-dc":artist("AC/DC",6,{members:["Angus Young"]}),
  "slash":artist("Slash",7,{}),
  "duff-mckagan":artist("Duff McKagan",8,{}),
  "guns-n-roses":artist("Guns N' Roses",9,{members:["Slash","Duff McKagan"]}),
  "ronnie-wood":artist("Ronnie Wood",10,{associatedActs:["The Rolling Stones","Faces"]}),
  "frank-beard":artist("Frank Beard",12,{associatedActs:["ZZ Top"],searchLinks:["ZZ Top"]}),
  "zz-top":artist("ZZ Top",13,{members:["Frank Beard"]}),
  "david-coverdale":artist("David Coverdale",14,{associatedActs:["Whitesnake"],searchLinks:["Whitesnake"]}),
  "whitesnake":artist("Whitesnake",15,{members:["David Coverdale"]}),
  "vinnie-stigma":artist("Vinnie Stigma",16,{associatedActs:["Agnostic Front"]}),
  "roger-miret":artist("Roger Miret",17,{associatedActs:["Agnostic Front"]}),
  "agnostic-front":artist("Agnostic Front",18,{members:["Vinnie Stigma","Roger Miret"]}),
  "john-mcgeoch":artist("John McGeoch",19,{associatedActs:["Public Image Ltd.","Magazine","Visage","Siouxsie and the Banshees"]}),
  "the-sheepdogs":artist("The Sheepdogs",20,{members:["Ewan Currie"]}),
  "ewan-currie":artist("Ewan Currie",21,{associatedActs:["The Sheepdogs"],searchLinks:["The Sheepdogs"]}),
  "robert-jon-the-wreck":artist("Robert Jon & The Wreck",22,{members:["Robert Jon Burrison"]}),
  "robert-jon-burrison":artist("Robert Jon Burrison",23,{associatedActs:["Robert Jon & The Wreck"],searchLinks:["Robert Jon & The Wreck"]}),
  "george-clinton":artist("George Clinton",24,{},true,["Parliament","Funkadelic"]),
  "bootsy-collins":artist("Bootsy Collins",25,{}),
  "maceo-parker":artist("Maceo Parker",26,{}),
  "fred-wesley":artist("Fred Wesley",27,{},true,["Fred Wesley Generations Trio","Generations Trio","Generations"]),
  "iggy-pop":artist("Iggy Pop",28,{}),
  "kyuss":artist("Kyuss",30,{members:[]},false),
  "p-funk":artist("P-Funk",32,{searchLinks:["George Clinton","Bootsy Collins","Maceo Parker","Fred Wesley"],searchAliasLinks:{"P-Funk All-Stars":["George Clinton"],"P-Funk Allstars":["George Clinton"]}},false,["P-Funk All-Stars","P-Funk Allstars"])
};
const relationshipNodes = {
  "faces":{n:"Faces",al:["The Faces"],identity:{members:["Ronnie Wood"],searchResultVisible:false}},
  "ron-mael":{n:"Ron Mael",al:[],identity:{searchLinks:["Sparks"]}},
  "russell-mael":{n:"Russell Mael",al:[],identity:{searchLinks:["Sparks"]}},
  "john-lydon":{n:"John Lydon",al:["Johnny Rotten"],identity:{searchAssociations:["Public Image Ltd."]}},
  "magazine":{n:"Magazine",al:[],identity:{formerMembers:["John McGeoch"],searchLinks:["John McGeoch"]}},
  "visage":{n:"Visage",al:[],identity:{formerMembers:["John McGeoch"],searchLinks:["John McGeoch"]}},
  "siouxsie-and-the-banshees":{n:"Siouxsie and the Banshees",al:[],identity:{formerMembers:["John McGeoch"],searchLinks:["John McGeoch"]}}
};
const terms = {};
Object.keys(artists).forEach((slug) => {
  terms[artists[slug].n] = slug;
  (artists[slug].al||[]).forEach((alias)=>{terms[alias]=slug;});
});
const sandbox = {window:{ElectricEyeArtistLookup:{terms},ElectricEyeContentIndex:{artists,articles,relationshipNodes}},document:{readyState:"loading",addEventListener:function(){}},console};
vm.createContext(sandbox);
vm.runInContext(source,sandbox);
const items = sandbox.__archiveTest.makeArtistItems();
function normalize(value) { return (value||"").toLowerCase(); }
function matches(query) {
  return sandbox.__archiveTest.filterItemsForQuery(items,query,true).map((item) => item.name);
}
function scoped(name,term) {
  const item=items.find((candidate)=>candidate.name===name);
  return item ? ((item.scopedArticleItems||{})[normalize(term)]||[]).map((article)=>article.name) : [];
}
const queries=["Mick Jagger","Geezer Butler","Angus Young","Slash","Duff McKagan","Guns N' Roses","Ronnie Wood","Faces","The Faces","Frank Beard","David Coverdale","Vinnie Stigma","Roger Miret","Agnostic Front","John McGeoch","Public Image Ltd.","The Sheepdogs","Ewan Currie","Robert Jon & The Wreck","Robert Jon Burrison","Louis Cole","Scary Goldings","Parliament","Funkadelic","P-Funk All-Stars","P-Funk","Fred Wesley","Fred Wesley Generations Trio","Generations Trio","Generations","Ron Mael","Russell Mael","Johnny Rotten","Kyuss"];
const result={}; queries.forEach((query)=>{result[query]=matches(query);});
process.stdout.write(JSON.stringify(result));
'''
        result = subprocess.run(
            [node, "-e", runner, str(ARCHIVE_INDEX)],
            check=True,
            capture_output=True,
            text=True,
        )
        matches = json.loads(result.stdout)

        expected = {
            "Mick Jagger": {"The Rolling Stones"},
            "Geezer Butler": {"Black Sabbath"},
            "Angus Young": {"AC/DC"},
            "Slash": {"Slash", "Guns N' Roses"},
            "Duff McKagan": {"Duff McKagan", "Guns N' Roses"},
            "Guns N' Roses": {"Guns N' Roses", "Slash", "Duff McKagan"},
            "Ronnie Wood": {"Ronnie Wood", "The Rolling Stones"},
            "Faces": {"Ronnie Wood"},
            "The Faces": {"Ronnie Wood"},
            "Frank Beard": {"Frank Beard", "ZZ Top"},
            "David Coverdale": {"David Coverdale", "Whitesnake"},
            "Vinnie Stigma": {"Vinnie Stigma", "Agnostic Front"},
            "Roger Miret": {"Roger Miret", "Agnostic Front"},
            "Agnostic Front": {"Agnostic Front", "Vinnie Stigma", "Roger Miret"},
            "John McGeoch": {"John McGeoch", "Public Image Ltd."},
            "Public Image Ltd.": {"Public Image Ltd.", "John McGeoch"},
            "The Sheepdogs": {"The Sheepdogs", "Ewan Currie"},
            "Ewan Currie": {"Ewan Currie", "The Sheepdogs"},
            "Robert Jon & The Wreck": {"Robert Jon & The Wreck", "Robert Jon Burrison"},
            "Robert Jon Burrison": {"Robert Jon Burrison", "Robert Jon & The Wreck"},
            "Louis Cole": {"Louis Cole"},
            "Scary Goldings": {"Scary Goldings"},
            "Parliament": {"George Clinton"},
            "Funkadelic": {"George Clinton"},
            "P-Funk All-Stars": {"George Clinton"},
            "P-Funk": {"George Clinton", "Bootsy Collins", "Maceo Parker", "Fred Wesley"},
            "Fred Wesley": {"Fred Wesley"},
            "Fred Wesley Generations Trio": {"Fred Wesley"},
            "Generations Trio": {"Fred Wesley"},
            "Generations": {"Fred Wesley"},
            "Ron Mael": {"Sparks"},
            "Russell Mael": {"Sparks"},
            "Johnny Rotten": {"Public Image Ltd."},
        }
        for query, expected_names in expected.items():
            self.assertEqual(expected_names, set(matches[query]), query)
