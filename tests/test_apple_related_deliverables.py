import re
import shutil
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
import sys
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables" / "apple-related"
THEME = OUT / "Electric-Eye-Theme.xml"
CODE = OUT / "Code.gs"
FIXTURE = ROOT / "tests" / "fixtures" / "apple-related" / "2026-06-12--keb-mo-bataclan-paris-june-12th-2026.html"


def run_javascript(source):
    node = shutil.which("node")
    if node:
        with tempfile.TemporaryDirectory() as directory:
            source_path = Path(directory) / "harness.js"
            source_path.write_text(source, encoding="utf-8")
            runner = (
                "const fs=require('fs'),vm=require('vm');"
                "const source=fs.readFileSync(process.argv[1],'utf8');"
                "const value=vm.runInNewContext(source,{console:{log:()=>{}}});"
                "if(value!==undefined)process.stdout.write(String(value));"
            )
            result = subprocess.run(
                [node, "-e", runner, str(source_path)],
                check=True,
                capture_output=True,
                text=True,
            )
        return result.stdout.strip()

    osascript = shutil.which("osascript")
    if osascript:
        with tempfile.TemporaryDirectory() as directory:
            source_path = Path(directory) / "harness.js"
            source_path.write_text(source, encoding="utf-8")
            result = subprocess.run(
                [osascript, "-l", "JavaScript", str(source_path)],
                check=True,
                capture_output=True,
                text=True,
            )
        return result.stdout.strip()

    raise RuntimeError("JavaScript tests require Node.js or macOS JavaScript for Automation")


def check_javascript_syntax(source, label):
    node = shutil.which("node")
    if node:
        with tempfile.TemporaryDirectory() as directory:
            source_path = Path(directory) / f"{label}.js"
            source_path.write_text(source, encoding="utf-8")
            subprocess.run(
                [node, "--check", str(source_path)],
                check=True,
                capture_output=True,
                text=True,
            )
        return

    osacompile = shutil.which("osacompile")
    if osacompile:
        with tempfile.TemporaryDirectory() as directory:
            source_path = Path(directory) / f"{label}.js"
            output_path = Path(directory) / f"{label}.scpt"
            source_path.write_text(source, encoding="utf-8")
            subprocess.run(
                [osacompile, "-l", "JavaScript", "-o", str(output_path), str(source_path)],
                check=True,
                capture_output=True,
                text=True,
            )
        return

    raise RuntimeError("JavaScript syntax checks require Node.js or macOS osacompile")


class AppleRelatedDeliverableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run(
            [sys.executable, str(ROOT / "tools/build_apple_related_deliverables.py")],
            cwd=ROOT,
            check=True,
        )
        cls.theme = THEME.read_text(encoding="utf-8")
        cls.code = CODE.read_text(encoding="utf-8")

    def run_apps_script(self, suffix):
        return run_javascript(self.code + "\n" + suffix)

    def test_theme_is_valid_xml_and_exposes_every_post_id(self):
        ET.parse(THEME)
        self.assertIn("expr:data-ee-post-id='data:post.id'", self.theme)
        self.assertNotIn("allowedPost", self.theme)

    def test_ready_payload_uses_positive_legacy_markers(self):
        self.assertIn('data-ee-legacy-apple-source', self.theme)
        self.assertIn('data-ee-legacy-apple-row', self.theme)
        self.assertIn('removeLegacySafeAffiliate();', self.theme)
        self.assertIn('if(!categories.length)return;', self.theme)
        self.assertIn('if(hasExistingSection())return;', self.theme)
        self.assertNotIn('querySelectorAll("[class*=sponsored]', self.theme)

    def test_keb_mo_fixture_contains_both_preserved_and_replaceable_apple_content(self):
        soup = BeautifulSoup(FIXTURE.read_text(encoding="utf-8"), "html.parser")
        legacy = [
            anchor
            for anchor in soup.select('a[href*="tv.apple.com"],a[href*="books.apple.com"]')
            if anchor.find("img")
        ]
        inline_music = [anchor for anchor in soup.select('a[href*="music.apple.com"]') if not anchor.find("img")]
        music_embeds = soup.select('iframe[src*="music.apple.com"],iframe[src*="embed.music.apple.com"]')
        unrelated_images = [
            image for image in soup.find_all("img")
            if not image.find_parent("a", href=re.compile(r"(?:tv|books)\.apple\.com"))
        ]
        self.assertGreater(len(legacy), 0)
        self.assertGreater(len(inline_music), 0)
        self.assertGreater(len(music_embeds), 0)
        self.assertGreater(len(unrelated_images), 0)
        self.assertIn('a[href*="tv.apple.com"],a[href*="books.apple.com"]', self.theme)
        self.assertNotIn('a[href*="music.apple.com"] img', self.theme)
        self.assertIn("ee-apple-music-embed-enhancer", self.theme)

    def test_keb_mo_positive_marker_replacement_preserves_editorial_content(self):
        soup = BeautifulSoup(FIXTURE.read_text(encoding="utf-8"), "html.parser")
        before_inline = len([a for a in soup.select('a[href*="music.apple.com"]') if not a.find("img")])
        before_embeds = len(soup.select('iframe[src*="music.apple.com"],iframe[src*="embed.music.apple.com"]'))
        before_photos = len([
            image for image in soup.find_all("img")
            if not image.find_parent("a", href=re.compile(r"(?:tv|books)\.apple\.com"))
        ])

        rows = []
        for anchor in soup.select('a[href*="tv.apple.com"],a[href*="books.apple.com"]'):
            if not anchor.find("img"):
                continue
            row = anchor.find_parent(class_="separator")
            if row is not None and row not in rows:
                rows.append(row)

        utilities = {
            "sponsored content",
            "sponsored item",
            "sponsored items",
            "click here to subscribe to apple tv",
            "subscribe to apple tv",
            "",
        }
        for row in rows:
            for direction in ("previous_sibling", "next_sibling"):
                node = getattr(row, direction)
                guard = 0
                while node is not None and guard < 6:
                    guard += 1
                    next_node = getattr(node, direction)
                    if not getattr(node, "name", None):
                        node = next_node
                        continue
                    has_media = node.select_one("img,iframe,video,audio,object,embed,form,table,ins.adsbygoogle")
                    text = " ".join(node.get_text(" ", strip=True).lower().split()).removesuffix(":")
                    if has_media or text not in utilities:
                        break
                    node.decompose()
                    node = next_node
            row.decompose()

        self.assertEqual(0, len(soup.select('a[href*="tv.apple.com"] img,a[href*="books.apple.com"] img')))
        self.assertNotIn("Sponsored content", soup.get_text(" ", strip=True))
        self.assertEqual(before_inline, len([a for a in soup.select('a[href*="music.apple.com"]') if not a.find("img")]))
        self.assertEqual(before_embeds, len(soup.select('iframe[src*="music.apple.com"],iframe[src*="embed.music.apple.com"]')))
        self.assertEqual(before_photos, len([
            image for image in soup.find_all("img")
            if not image.find_parent("a", href=re.compile(r"(?:tv|books)\.apple\.com"))
        ]))

    def test_empty_or_disabled_response_leaves_legacy_fallback(self):
        self.assertRegex(self.theme, r"if\(!CONFIG\.enabled\|\|!context\|\|!postBody\)return")
        self.assertRegex(self.theme, r"if\(!categories\.length\)return;\s*removeLegacySafeAffiliate\(\);")
        self.assertIn('output=eePublicPayload_(eeGetPayload_(params.postId))||output;', self.code)
        self.assertIn('settings.enabled && /^[0-9]+$/.test', self.code)

    def test_reader_endpoint_only_serves_stored_ready_payloads(self):
        do_get = self.code[self.code.index("function doGet(") : self.code.index("function eeBackfillWorker(")]
        self.assertIn("eeGetPayload_", do_get)
        self.assertNotIn("eeAppleSearch_", do_get)
        self.assertNotIn("eeGeneratePayload_", do_get)

    def test_worker_is_bounded_resumable_and_has_no_trigger_api(self):
        self.assertIn("function eeBackfillWorker()", self.code)
        self.assertIn("safeStartCutoff=started+180000", self.code)
        self.assertIn('EE_APPLE_BACKFILL_INDEX', self.code)
        self.assertIn("if(stalled>=2)break", self.code)
        self.assertIn("function eeBackfillStatus()", self.code)
        self.assertIn("retryCount>=2", self.code)
        self.assertNotIn("ScriptApp.newTrigger", self.code)
        self.assertNotIn("ScriptApp.getProjectTriggers", self.code)

    def test_schema_upgrade_is_backward_compatible_and_debug_debris_removed(self):
        self.assertIn('sheet.getLastColumn() < 8', self.code)
        self.assertIn('setValue("retryCount")', self.code)
        for name in (
            "eeRetryBackfillFrom9",
            "eeDebugBackfill9",
            "eeDebugSignals9",
            "eeDebugAnalysis9",
            "eeFinalTest9",
        ):
            self.assertNotIn(name, self.code)

    def test_multi_artist_query_plan_guard_remains(self):
        self.assertIn("if ((analysis.primaryArtists || []).length > 1)", self.code)
        self.assertIn('query.intent === "ARTIST"', self.code)
        self.assertIn("primarySet[eeNorm_(query.term || \"\")]", self.code)

        harness = self.code + r'''
eeCachedEntityProfile_=function(){return null;};
eeAcquireEntityProfile_=function(){return null;};
eeAppleLabelFallbackArtists_=function(){return ["in flames","trivium"];};
var regressionPost={id:"1",title:"In Flames & Trivium Join Forces for Massive European Tour — Paris Date Announced",labels:["In Flames","Trivium"],content:"",url:""};
JSON.stringify(eeEntityHints_(regressionPost).primaryArtists);
'''
        self.assertEqual('["In Flames","Trivium"]', run_javascript(harness))

    def test_reviewed_floor_and_dolly_subjects_are_exact(self):
        result = self.run_apps_script(r'''
var registry={schemaVersion:1,artists:[
  {canonicalName:"Floor Jansen",slug:"floor-jansen",articleIds:[]},
  {canonicalName:"Dolly Parton",slug:"dolly-parton",articleIds:[]}
],articleOverrides:{
  "3124541008960499514":{primaryArtists:["Floor Jansen"],identityEvidence:["reviewed"]},
  "4579274501673632187":{primaryArtists:["Dolly Parton"],identityEvidence:["reviewed"]}
}};
JSON.stringify([
  eeFastArticleIdentity_({id:"3124541008960499514",title:"Floor Jansen releases new video + tour dates including Paris!"},registry).primaryArtists,
  eeFastArticleIdentity_({id:"4579274501673632187",title:"Friday's Playlist: Dolly Rocks"},registry).primaryArtists
]);
''')
        self.assertEqual('[["Floor Jansen"],["Dolly Parton"]]', result)

    def test_fast_identity_regression_matrix_and_ambiguous_names(self):
        result = self.run_apps_script(r'''
var registry={schemaVersion:1,structuralLabels:["obituary","news","concert review"],articleOverrides:{},artists:[
 {canonicalName:"Obituary",slug:"obituary",aliases:[],articleIds:[],ambiguityClass:"distinctive"},
 {canonicalName:"Sparks",slug:"sparks",aliases:[],articleIds:[],ambiguityClass:"common_word",members:["Ron Mael","Russell Mael"]},
 {canonicalName:"BEAT",slug:"beat",aliases:[],articleIds:[],ambiguityClass:"common_word",members:["Adrian Belew","Tony Levin","Steve Vai","Danny Carey"],associatedActs:["King Crimson"],keywords:["THRAK"]},
 {canonicalName:"Down",slug:"down",aliases:[],articleIds:[],ambiguityClass:"common_word"},
 {canonicalName:"Possessed",slug:"possessed",aliases:[],articleIds:[],ambiguityClass:"common_word"},
 {canonicalName:"The Cure",slug:"the-cure",aliases:[],articleIds:["known-cure"],ambiguityClass:"distinctive"},
 {canonicalName:"Shadow Of Intent",slug:"shadow-of-intent",aliases:[],articleIds:[],ambiguityClass:"distinctive"},
 {canonicalName:"Kris Barras Band",slug:"kris-barras-band",aliases:[],articleIds:[],ambiguityClass:"distinctive"},
 {canonicalName:"Monty Alexander",slug:"monty-alexander",aliases:[],articleIds:[],ambiguityClass:"distinctive"},
 {canonicalName:"Killer Kin",slug:"killer-kin",aliases:[],articleIds:[],ambiguityClass:"distinctive"},
 {canonicalName:"GA-20",slug:"ga-20",aliases:[],articleIds:[],ambiguityClass:"distinctive"},
 {canonicalName:"Anthrax",slug:"anthrax",aliases:[],articleIds:[],ambiguityClass:"distinctive"},
 {canonicalName:"Hackett & Rothery",slug:"hackett-rothery",aliases:[],articleIds:[],ambiguityClass:"distinctive"},
 {canonicalName:"Frank Beard",slug:"frank-beard",aliases:[],articleIds:[],ambiguityClass:"distinctive",associatedActs:["ZZ Top"]}
]};
function keys(post){return eeFastArticleIdentity_(post,registry).primaryArtistKeys;}
JSON.stringify({
  ordinary:keys({id:"1",title:"How to beat the heat",labels:[],content:""}),
  obituaryMetadata:keys({id:"obit-meta",title:"Frank Beard, ZZ Top drummer, dies aged 76",labels:["News","Obituary"],content:""}),
  obituaryBand:keys({id:"obit-band",title:"Obituary announce a new album",labels:["News","Obituary"],content:""}),
 ambiguousTitle:keys({id:"2",title:"BEAT returns",labels:[],content:""}),
 sparks:keys({id:"3",title:"Sparks return",labels:["Sparks"],content:"Ron Mael and Russell Mael discuss the record."}),
 beat:keys({id:"4",title:"BEAT announce Paris",labels:["BEAT","Adrian Belew","Tony Levin"],content:"Steve Vai revisits King Crimson and THRAK."}),
 down:keys({id:"5",title:"Down return",labels:["Down"],content:"Down make a new record. Down tour next year."}),
 possessed:keys({id:"6",title:"Possessed return",labels:["Possessed"],content:"Possessed recorded again. Possessed will tour."}),
 known:keys({id:"known-cure",title:"Festival news",labels:[],content:""}),
 multi:keys({id:"7",title:"Anthrax and GA-20 announce dates",labels:["Anthrax","GA-20"],content:""}),
 distinct:["Shadow Of Intent","Monty Alexander","Killer Kin","Hackett & Rothery"].map(function(name){return keys({id:"d"+name,title:name+" announce dates",labels:[name],content:""})[0];}),
 concert:keys({id:"8",title:"Kris Barras Band @ Le Trianon",labels:["Kris Barras Band"],content:""}),
 obituary:keys({id:"9",title:"R.I.P. Frank Beard",labels:["Frank Beard"],content:"The ZZ Top drummer has died."}),
 festival:keys({id:"10",title:"Full festival lineup announced",labels:["Festival","News"],content:"Many artists play."}),
 provisional:keys({id:"11",title:"New Artist @ La Maroquinerie",labels:["New Artist"],content:""})
});
''')
        self.assertEqual(
            '{"ordinary":[],"obituaryMetadata":["frank-beard"],"obituaryBand":["obituary"],"ambiguousTitle":[],"sparks":["sparks"],"beat":["beat"],'
            '"down":["down"],"possessed":["possessed"],"known":["the-cure"],'
            '"multi":["anthrax","ga-20"],"distinct":["shadow-of-intent","monty-alexander","killer-kin","hackett-rothery"],"concert":["kris-barras-band"],'
            '"obituary":["frank-beard"],"festival":[],"provisional":["new-artist"]}',
            result,
        )

    def test_artist_catalogue_reuse_avoids_repeat_discovery(self):
        result = self.run_apps_script(r'''
var registry={schemaVersion:1,articleOverrides:{},artists:[{canonicalName:"Sparks",slug:"sparks",aliases:[],articleIds:["1","2"],ambiguityClass:"common_word"}]};
eeArtistRegistry_=function(){return registry;};eePutArticleIdentity_=function(){};
var discovery=0,record={artistKey:"sparks",canonicalName:"Sparks",appleArtistId:"99",identityConfidence:"HIGH",status:"RESOLVED",catalogue:{categories:[{category:"LISTEN",items:[{stableId:"album",title:"Album",relevanceScore:100}]}]}};
eeGetArtistCatalogue_=function(){return record;};eeDiscoverArtistCatalogue_=function(){discovery+=1;return record;};
eeAppleSettings_=function(){return {storefront:"FR"};};
var first=eeGeneratePayload_({id:"1",title:"Sparks",labels:[],content:"",url:"/1"});
var second=eeGeneratePayload_({id:"2",title:"Sparks",labels:[],content:"",url:"/2"});
JSON.stringify({discovery:discovery,first:first.categories[0].items.length,second:second.categories[0].items.length,version:second.generationVersion});
''')
        self.assertEqual('{"discovery":0,"first":1,"second":1,"version":3}', result)

    def test_minimal_pending_catalogue_is_ready_without_waiting_for_related_artist(self):
        result = self.run_apps_script(r'''
var puts=[],discoveries=[];
eeAppleSettings_=function(){return {enabled:true,storefront:"FR"};};
eeArtistRegistry_=function(){return {schemaVersion:1,articleOverrides:{},structuralLabels:[],artists:[
 {canonicalName:"Primary",slug:"primary",aliases:[],articleIds:["1"],ambiguityClass:"distinctive"},
 {canonicalName:"Related",slug:"related",aliases:[],articleIds:["1"],ambiguityClass:"distinctive"}
]};};
eePutArticleIdentity_=function(){};eeGetArtistCatalogue_=function(){return null;};
eeDiscoverArtistCatalogue_=function(artist){discoveries.push(artist.slug);if(artist.slug==="related")throw new Error("RELATED_MUST_NOT_BLOCK");return {artistKey:"primary",canonicalName:"Primary",appleArtistId:"99",status:"RESOLVED",catalogue:{categories:[{category:"LISTEN",items:[{stableId:"album",title:"Album",creator:"Primary"}]}],enrichment:{status:"PENDING"}}};};
eePutPayload_=function(post,payload,status){puts.push({status:status,payload:payload});};
var payload=eeProcessPost_({id:"1",title:"Primary and Related",labels:[],content:"",url:"/1"});
JSON.stringify({status:puts[0].status,discoveries:discoveries,items:payload.categories[0].items.length,enrichmentRequired:!!payload.enrichment});
''')
        self.assertEqual(
            '{"status":"READY","discoveries":["primary"],"items":1,"enrichmentRequired":false}',
            result,
        )

    def test_last_known_good_ready_rejects_empty_error_and_poorer_payload(self):
        result = self.run_apps_script(r'''
var existing={storefront:"FR",categories:[{category:"LISTEN",items:[{stableId:"a"},{stableId:"b"}]},{category:"WATCH",items:[{stableId:"v"}]}]},writes=[];
eeGetPayload_=function(){return existing;};eeEncodePayloadCell_=function(value){return JSON.stringify(value);};
eePayloadSheet_=function(){return {getDataRange:function(){return {getValues:function(){return [["header"]];}};},getRange:function(){return {setValues:function(rows){writes.push(rows[0]);}};}};};
CacheService={getScriptCache:function(){return {remove:function(){}};}};
var post={id:"1",url:"/1"};
var empty=eePutPayload_(post,{storefront:"FR",categories:[]},"EMPTY","none",0);
var error=eePutPayload_(post,{storefront:"FR",categories:[]},"ERROR","failed",0);
var poorer=eePutPayload_(post,{storefront:"FR",categories:[{category:"LISTEN",items:[{stableId:"a"}]}]},"READY","",0);
var richer=eePutPayload_(post,{storefront:"FR",categories:[{category:"LISTEN",items:[{stableId:"a"},{stableId:"b"},{stableId:"c"}]},{category:"WATCH",items:[{stableId:"v"}]}]},"READY","",0);
JSON.stringify({empty:empty,error:error,poorer:poorer,writes:writes.length,lastStatus:writes[0][5]});
''')
        self.assertEqual(
            '{"empty":false,"error":false,"poorer":false,"writes":1,"lastStatus":"READY"}',
            result,
        )

    def test_minimal_ready_round_trips_through_existing_reader_boundary(self):
        result = self.run_apps_script(r'''
var rows=[["postId","canonicalUrl","generatedAt","storefront","payloadJson","status","error","retryCount"]];
var sheet={getLastRow:function(){return rows.length-1;},getLastColumn:function(){return 8;},getDataRange:function(){return {getValues:function(){return rows;}};},getRange:function(row){return {setValues:function(values){rows[row-1]=values[0];},setValue:function(){}};}};
eePayloadSheet_=function(){return sheet;};eeEncodePayloadCell_=function(value){return JSON.stringify(value);};eeDecodePayloadCell_=function(value){return JSON.parse(value);};
var cache={};CacheService={getScriptCache:function(){return {get:function(key){return cache[key]||null;},put:function(key,value){cache[key]=value;},remove:function(key){delete cache[key];}};}};
eeAppleSettings_=function(){return {enabled:true,storefront:"FR"};};eeApplePostAllowed_=function(){return true;};
eeGeneratePayload_=function(post){return {schemaVersion:1,generationVersion:3,postId:String(post.id),storefront:"FR",categories:[{category:"LISTEN",items:[{stableId:"album",title:"Album"}]}],diagnostics:{enrichment:"PENDING"}};};
ContentService={MimeType:{JSON:"JSON",JAVASCRIPT:"JS"},createTextOutput:function(text){return {text:text,setMimeType:function(){return this;}};}};
eeProcessPost_({id:"42",url:"/article"});
var stored=eeGetPayload_("42"),response=JSON.parse(doGet({parameter:{action:"payload",postId:"42"}}).text);
JSON.stringify({status:rows[1][5],stored:stored.categories[0].items[0].stableId,served:response.categories[0].items[0].stableId,diagnostics:Object.prototype.hasOwnProperty.call(response,"diagnostics")});
''')
        self.assertEqual(
            '{"status":"READY","stored":"album","served":"album","diagnostics":false}',
            result,
        )

    def test_no_subject_article_does_not_block_later_ready_article(self):
        result = self.run_apps_script(r'''
var props={EE_APPLE_ASSEMBLY_INDEX:"1"},writes=[];
PropertiesService={getScriptProperties:function(){return {getProperty:function(key){return props[key]||"";},setProperty:function(key,value){props[key]=value;}};}};
eeAcquireWorkerLease_=function(){return true;};eeReleaseWorkerLease_=function(){};
eeArticleIdentitySheet_=function(){return {getDataRange:function(){return {getValues:function(){return [["header"],["empty","",0,1,"[]","[]","NONE",false,"","other"],["ready","",0,1,'["artist"]','["Artist"]',"HIGH",false,"","other"]];}};}};};
eeGetArtistCatalogue_=function(key){return key==="artist"?{status:"RESOLVED",catalogue:{categories:[{category:"LISTEN",items:[{stableId:"album",title:"Album"}]}],enrichment:{status:"PENDING"}}}:null;};
eeFetchPostById_=function(id){return {id:id,title:id,url:"/"+id,content:""};};eeAppleSettings_=function(){return {storefront:"FR"};};
eePutPayload_=function(post,payload,status){writes.push([post.id,status]);};
var worker=eeAssembleArticlePayloadsWorker();JSON.stringify({processed:worker.processed,writes:writes,cursor:props.EE_APPLE_ASSEMBLY_INDEX});
''')
        self.assertEqual(
            '{"processed":2,"writes":[["empty","EMPTY"],["ready","READY"]],"cursor":"3"}',
            result,
        )

    def test_article_context_reranks_cached_items_without_mutating_catalogue(self):
        result = self.run_apps_script(r'''
eeAppleSettings_=function(){return {storefront:"FR"};};
var source={categories:[{category:"LISTEN",items:[
 {stableId:"other",title:"Other Album",relevanceScore:100},
 {stableId:"focus",title:"Focus Album",relevanceScore:96}
]}]},analysis={primaryArtistKeys:["artist"],primaryArtists:["Artist"],people:[],identityConfidence:"HIGH",articleType:"album_review"};
var payload=eeAssemblePayloadFromCatalogues_({id:"1",title:"Album Review: Artist - Focus Album",content:"",url:""},analysis,[{catalogue:source}]);
JSON.stringify({order:payload.categories[0].items.map(function(item){return item.stableId;}),cached:source.categories[0].items[1].relevanceScore});
''')
        self.assertEqual('{"order":["focus","other"],"cached":96}', result)

    def test_upsert_is_idempotent_for_migration_rows(self):
        result = self.run_apps_script(r'''
var values=[["artistKey"],["sparks"]],writes=[];
var sheet={getDataRange:function(){return {getValues:function(){return values;}};},getRange:function(row,col,height,width){return {setValues:function(rows){writes.push(row);values[row-1]=rows[0];}};}};
eeUpsertRow_(sheet,0,"sparks",["sparks","Sparks"]);
eeUpsertRow_(sheet,0,"sparks",["sparks","Sparks updated"]);
JSON.stringify({writes:writes,rows:values.length,value:values[1][1]});
''')
        self.assertEqual('{"writes":[2,2],"rows":2,"value":"Sparks updated"}', result)

    def test_generation_two_seed_is_idempotent_and_selective(self):
        result = self.run_apps_script(r'''
var payload={schemaVersion:1,generationVersion:2,postId:"1",subject:{primaryArtists:["Sparks"]},identity:{level:"HIGH",artistId:"99"},categories:[{category:"LISTEN",items:[{stableId:"album"}]}]};
eePayloadSheet_=function(){return {getDataRange:function(){return {getValues:function(){return [["header"],["1","","","","encoded","READY"]];}};}};};
eeDecodePayloadCell_=function(){return payload;};eeArtistRegistry_=function(){return {artists:[{canonicalName:"Sparks",slug:"sparks"}]};};
var stored=null,puts=0;eeGetArtistCatalogue_=function(){return stored;};eePutArtistCatalogue_=function(record){puts+=1;stored=record;};
var first=eeSeedArtistCataloguesFromGeneration2(),second=eeSeedArtistCataloguesFromGeneration2();
JSON.stringify({first:first.seeded,second:second.seeded,puts:puts,status:stored.status});
''')
        self.assertEqual('{"first":1,"second":0,"puts":1,"status":"RESOLVED"}', result)

    def test_artist_discovery_has_per_artist_concurrency_lease(self):
        self.assertIn('var lease="CATALOGUE_"', self.code)
        self.assertIn('new Error("ARTIST_DISCOVERY_BUSY")', self.code)
        self.assertIn("eeReleaseWorkerLease_(lease)", self.code)

    def test_artist_discovery_emits_compact_per_artist_diagnostics(self):
        result = self.run_apps_script(r'''
var logs=[];console.log=function(value){logs.push(value);};
var saved=null,properties={};
eeAcquireWorkerLease_=function(){return true;};eeReleaseWorkerLease_=function(){};
eeGetArtistCatalogue_=function(){return {status:"UNRESOLVED"};};
eeGeneratePayloadLegacy_=function(){
  var query=eeDiscoveryDiagnosticQuery_({term:"Sparks",entity:"musicArtist",category:"LISTEN"});
  eeDiscoveryDiagnosticAppleCall_();eeDiscoveryDiagnosticCacheHit_();
  eeDiscoveryDiagnosticCandidates_(query,{results:[{},{}]});
  eeDiscoveryDiagnosticDecision_(query,true,"QUALIFYING_RELATIONSHIP");
  eeDiscoveryDiagnosticDecision_(query,false,"NO_QUALIFYING_RELATIONSHIP");
  return {identity:{level:"HIGH",artistId:"99"},categories:[]};
};
eePutArtistCatalogue_=function(record){saved=record;};
PropertiesService={getScriptProperties:function(){return {getProperty:function(key){return properties[key]||"";},setProperty:function(key,value){properties[key]=value;}};}};
var record=eeDiscoverArtistCatalogue_({slug:"sparks",canonicalName:"Sparks"},{id:"post-1"},true);
var log=JSON.parse(logs[0]);
JSON.stringify({status:record.status,count:logs.length,type:log.type,artistKey:log.artistKey,canonicalName:log.canonicalName,appleCalls:log.appleCalls,cacheHits:log.cacheHits,terminalStatus:log.terminalStatus,terminalReason:log.terminalReason,stoppedBy:log.stoppedBy,elapsedIsNumber:typeof log.elapsedMs==="number",query:log.queries[0]});
''')
        self.assertEqual(
            '{"status":"RESOLVED","count":1,"type":"APPLE_ARTIST_DISCOVERY","artistKey":"sparks",'
            '"canonicalName":"Sparks","appleCalls":1,"cacheHits":1,"terminalStatus":"RESOLVED",'
            '"terminalReason":"CONFIDENT_MATCH","stoppedBy":"","elapsedIsNumber":true,'
            '"query":{"term":"Sparks","entity":"musicArtist","category":"LISTEN","candidateCount":2,'
            '"accepted":1,"rejected":1,"reasons":{"QUALIFYING_RELATIONSHIP":1,"NO_QUALIFYING_RELATIONSHIP":1}}}',
            result,
        )

    def test_artist_discovery_diagnostics_report_retry_stop_without_changing_error(self):
        result = self.run_apps_script(r'''
var logs=[];console.log=function(value){logs.push(value);};
eeAcquireWorkerLease_=function(){return true;};eeReleaseWorkerLease_=function(){};
eeGetArtistCatalogue_=function(){return {status:"UNRESOLVED"};};
eeGeneratePayloadLegacy_=function(){var error=new Error("APPLE_SEARCH_HTTP_429");error.code="APPLE_SEARCH_HTTP_429";error.retryable=true;throw error;};
var caught=null;try{eeDiscoverArtistCatalogue_({slug:"artist",canonicalName:"Artist"},{id:"post-1"},true);}catch(error){caught={code:error.code,retryable:error.retryable};}
var log=JSON.parse(logs[0]);
var stops=["APPLE_SEARCH_HTTP_403","APPLE_SEARCH_HTTP_429","APPLE_SEARCH_EXECUTION_HEADROOM","APPLE_RETRY_LATER_COOLDOWN"].map(function(code){return eeDiscoveryDiagnosticStopReason_({code:code});});
JSON.stringify({caught:caught,count:logs.length,status:log.terminalStatus,reason:log.terminalReason,stoppedBy:log.stoppedBy,stops:stops});
''')
        self.assertEqual(
            '{"caught":{"code":"APPLE_SEARCH_HTTP_429","retryable":true},"count":1,'
            '"status":"RETRY_LATER","reason":"APPLE_SEARCH_HTTP_429","stoppedBy":"429",'
            '"stops":["403","429","HEADROOM","COOLDOWN"]}',
            result,
        )

    def test_artist_discovery_diagnostics_are_wired_to_existing_calls_only(self):
        self.assertIn("eeDiscoveryDiagnosticAppleCall_();\n      var response=UrlFetchApp.fetch(url,options);", self.code)
        self.assertEqual(2, self.code.count("if(cached){eeDiscoveryDiagnosticCacheHit_();"))
        self.assertIn("var queryDiagnostic=eeDiscoveryDiagnosticQuery_(query);", self.code)
        self.assertIn("eeDiscoveryDiagnosticCandidates_(queryDiagnostic,response);", self.code)

    def test_clear_primary_artist_resolves_before_exhaustive_enrichment(self):
        result = self.run_apps_script(r'''
var saved=null,legacyCalls=0,searches=[],properties={};
eeAcquireWorkerLease_=function(){return true;};eeReleaseWorkerLease_=function(){};
eeGetArtistCatalogue_=function(){return {status:"UNRESOLVED"};};
eeArticleAnalysis_=function(){return {relationshipGraph:{nodes:[],edges:[]}};};
eeAppleSettings_=function(){return {storefront:"FR"};};
eeAppleSearch_=function(query){searches.push(query);return {results:[1,2,3].map(function(id){return {artistId:"99",artistName:"Ariel Pink",collectionId:id,collectionName:"Album "+id};})};};
eeAddCandidateToMap_=function(map,raw){map[String(raw.collectionId)]={stableId:String(raw.collectionId),category:"LISTEN",creator:raw.artistName,appleArtistId:raw.artistId,title:raw.collectionName,relevanceScore:96};return true;};
eeGeneratePayloadLegacy_=function(){legacyCalls+=1;throw new Error("EXHAUSTIVE_PATH_SHOULD_NOT_RUN");};
eePutArtistCatalogue_=function(record){saved=record;};
PropertiesService={getScriptProperties:function(){return {getProperty:function(key){return properties[key]||"";},setProperty:function(key,value){properties[key]=value;}};}};
var record=eeDiscoverArtistCatalogue_({slug:"ariel-pink",canonicalName:"Ariel Pink"},{id:"post-1"});
JSON.stringify({status:record.status,artistId:record.appleArtistId,confidence:record.identityConfidence,searchCount:searches.length,query:{term:searches[0].term,entity:searches[0].entity,category:searches[0].category},legacyCalls:legacyCalls,staleImmediately:Date.parse(saved.staleAfter)<=Date.now(),schemaVersion:record.catalogue.schemaVersion,generationVersion:record.catalogue.generationVersion,categories:record.catalogue.categories.length});
''')
        self.assertEqual(
            '{"status":"RESOLVED","artistId":"99","confidence":"HIGH","searchCount":1,'
            '"query":{"term":"Ariel Pink","entity":"album","category":"LISTEN"},"legacyCalls":0,'
            '"staleImmediately":true,"schemaVersion":1,"generationVersion":3,"categories":1}',
            result,
        )

    def test_ambiguous_primary_artist_uses_existing_deep_fallback(self):
        result = self.run_apps_script(r'''
var saved=null,legacyCalls=0,searches=0,properties={};
eeAcquireWorkerLease_=function(){return true;};eeReleaseWorkerLease_=function(){};
eeGetArtistCatalogue_=function(){return {status:"UNRESOLVED"};};
eeArticleAnalysis_=function(){return {relationshipGraph:{nodes:[],edges:[]}};};
eeAppleSettings_=function(){return {storefront:"FR"};};
eeAppleSearch_=function(){searches+=1;var rows=[];["11","22"].forEach(function(artistId){[1,2,3].forEach(function(id){rows.push({artistId:artistId,artistName:"Nails",collectionId:artistId+id,collectionName:"Album"});});});return {results:rows};};
eeAddCandidateToMap_=function(){return true;};
eeGeneratePayloadLegacy_=function(){legacyCalls+=1;return {identity:{level:"MODERATE",artistId:null},categories:[]};};
eePutArtistCatalogue_=function(record){saved=record;};
PropertiesService={getScriptProperties:function(){return {getProperty:function(key){return properties[key]||"";},setProperty:function(key,value){properties[key]=value;}};}};
var record=eeDiscoverArtistCatalogue_({slug:"nails",canonicalName:"Nails"},{id:"post-1"});
JSON.stringify({status:record.status,confidence:record.identityConfidence,primarySearches:searches,legacyCalls:legacyCalls,error:record.error});
''')
        self.assertEqual(
            '{"status":"AMBIGUOUS","confidence":"MODERATE","primarySearches":1,"legacyCalls":1,"error":""}',
            result,
        )

    def test_forced_refresh_preserves_full_associated_act_enrichment(self):
        result = self.run_apps_script(r'''
var saved=null,fastCalls=0,legacyCalls=0,properties={};
eeAcquireWorkerLease_=function(){return true;};eeReleaseWorkerLease_=function(){};
eeGetArtistCatalogue_=function(){return {status:"RESOLVED"};};
eePrimaryArtistIdentityPayload_=function(){fastCalls+=1;throw new Error("FAST_PATH_SHOULD_NOT_RUN");};
eeGeneratePayloadLegacy_=function(){legacyCalls+=1;return {identity:{level:"HIGH",artistId:"99"},categories:[{category:"WATCH",items:[{stableId:"associated",creator:"King Crimson",title:"Associated act film"}]}]};};
eePutArtistCatalogue_=function(record){saved=record;};
PropertiesService={getScriptProperties:function(){return {getProperty:function(key){return properties[key]||"";},setProperty:function(key,value){properties[key]=value;}};}};
var record=eeDiscoverArtistCatalogue_({slug:"beat",canonicalName:"BEAT",associatedActs:["King Crimson"]},{id:"post-1"},true);
JSON.stringify({status:record.status,fastCalls:fastCalls,legacyCalls:legacyCalls,category:record.catalogue.categories[0].category,item:record.catalogue.categories[0].items[0].stableId,staleAfter:saved.staleAfter||""});
''')
        self.assertEqual(
            '{"status":"RESOLVED","fastCalls":0,"legacyCalls":1,"category":"WATCH",'
            '"item":"associated","staleAfter":""}',
            result,
        )

    def test_resolved_enrichment_headroom_preserves_identity_and_partial_catalogue(self):
        result = self.run_apps_script(r'''
var saved=null,properties={},calls=[];
eeAcquireWorkerLease_=function(){return true;};eeReleaseWorkerLease_=function(){};
var existing={artistKey:"maceo-parker",canonicalName:"Maceo Parker",appleArtistId:"42",identityConfidence:"HIGH",status:"RESOLVED",musicBrainzId:"mb",catalogue:{categories:[],enrichment:{status:"PENDING",completedQueries:[],totalQueries:2,pendingQueries:2}}};
eeGetArtistCatalogue_=function(){return existing;};
eeArticleAnalysis_=function(){return {primaryArtists:["Maceo Parker"],people:[],associatedPeople:[],existingAppleArtistIds:["42"],relationshipGraph:{nodes:[],edges:[]}};};
eeAppleSettings_=function(){return {storefront:"FR"};};
eeSearchPlan_=function(){return [{category:"LISTEN",media:"music",entity:"album",term:"Maceo Parker",intent:"ARTIST",storefront:"FR"},{category:"WATCH",media:"music",entity:"musicVideo",term:"Maceo Parker",intent:"ARTIST",storefront:"FR"}];};
eeAppleSearch_=function(query){calls.push(query.category);if(query.category==="WATCH"){var error=new Error("APPLE_SEARCH_EXECUTION_HEADROOM");error.code="APPLE_SEARCH_EXECUTION_HEADROOM";error.retryable=true;throw error;}return {results:[{artistId:"42",artistName:"Maceo Parker",collectionId:"album-1",collectionName:"Life on Planet Groove"}]};};
eeAddCandidateToMap_=function(map,raw,query){map[query.category+":"+raw.collectionId]={stableId:raw.collectionId,category:query.category,creator:raw.artistName,title:raw.collectionName,relevanceScore:96};return true;};
eePutArtistCatalogue_=function(record){saved=record;};
PropertiesService={getScriptProperties:function(){return {getProperty:function(key){return properties[key]||"";},setProperty:function(key,value){properties[key]=value;}};}};
var record=eeDiscoverArtistCatalogue_({slug:"maceo-parker",canonicalName:"Maceo Parker"},{id:"post-1"},true);
JSON.stringify({status:record.status,artistId:record.appleArtistId,confidence:record.identityConfidence,error:record.error,calls:calls,categories:record.catalogue.categories.map(function(group){return [group.category,group.items.length];}),enrichment:record.catalogue.enrichment,savedStatus:saved.status});
''')
        self.assertEqual(
            '{"status":"RESOLVED","artistId":"42","confidence":"HIGH",'
            '"error":"APPLE_SEARCH_EXECUTION_HEADROOM","calls":["LISTEN","WATCH"],'
            '"categories":[["LISTEN",1]],"enrichment":{"status":"PENDING",'
            '"completedQueries":["LISTEN|music|album|maceo parker|FR"],"totalQueries":2,'
            '"pendingQueries":1,"lastError":"APPLE_SEARCH_EXECUTION_HEADROOM"},"savedStatus":"RESOLVED"}',
            result,
        )

    def test_partial_enrichment_resumes_after_completed_query(self):
        result = self.run_apps_script(r'''
var saved=null,properties={},calls=[];EE_APPLE_ENRICHMENT_QUERIES_PER_RUN=1;
eeAcquireWorkerLease_=function(){return true;};eeReleaseWorkerLease_=function(){};
var existing={artistKey:"artist",canonicalName:"Artist",appleArtistId:"42",identityConfidence:"HIGH",status:"RESOLVED",catalogue:{categories:[],enrichment:{status:"PENDING",completedQueries:[],totalQueries:3,pendingQueries:3}}};
eeGetArtistCatalogue_=function(){return existing;};eeArticleAnalysis_=function(){return {primaryArtists:["Artist"],relationshipGraph:{nodes:[],edges:[]}};};eeAppleSettings_=function(){return {storefront:"FR"};};
eeSearchPlan_=function(){return ["LISTEN","WATCH","READ"].map(function(category){return {category:category,media:category==="READ"?"ebook":"music",entity:category==="LISTEN"?"album":category==="WATCH"?"musicVideo":"ebook",term:"Artist",intent:"ARTIST",storefront:"FR"};});};
eeAppleSearch_=function(query){calls.push(query.category);return {results:[{artistId:"42",artistName:"Artist",collectionId:query.category,collectionName:query.category}]};};
eeAddCandidateToMap_=function(map,raw,query){map[query.category+":"+raw.collectionId]={stableId:raw.collectionId,category:query.category,creator:raw.artistName,title:raw.collectionName,relevanceScore:96};return true;};
eePutArtistCatalogue_=function(record){saved=record;};PropertiesService={getScriptProperties:function(){return {getProperty:function(key){return properties[key]||"";},setProperty:function(key,value){properties[key]=value;}};}};
var first=eeDiscoverArtistCatalogue_({slug:"artist",canonicalName:"Artist"},{id:"post"},true);existing={artistKey:saved.artistKey,canonicalName:saved.canonicalName,appleArtistId:saved.appleArtistId,identityConfidence:saved.identityConfidence,status:saved.status,catalogue:saved.catalogue||{categories:saved.categories,enrichment:saved.enrichment}};existing.catalogue={categories:saved.categories,enrichment:saved.enrichment};
var second=eeDiscoverArtistCatalogue_({slug:"artist",canonicalName:"Artist"},{id:"post"},true);
JSON.stringify({calls:calls,firstCompleted:first.enrichment.completedQueries,secondCompleted:second.enrichment.completedQueries,categories:second.categories.map(function(group){return group.category;})});
''')
        self.assertEqual(
            '{"calls":["LISTEN","WATCH"],"firstCompleted":["LISTEN|music|album|artist|FR"],'
            '"secondCompleted":["LISTEN|music|album|artist|FR","WATCH|music|musicVideo|artist|FR"],'
            '"categories":["LISTEN","WATCH"]}',
            result,
        )

    def test_resolved_finalization_transport_failure_cannot_defer_identity(self):
        result = self.run_apps_script(r'''
var saved=null,properties={};eeAcquireWorkerLease_=function(){return true;};eeReleaseWorkerLease_=function(){};
var existing={artistKey:"artist",canonicalName:"Artist",appleArtistId:"42",identityConfidence:"HIGH",status:"RESOLVED",catalogue:{categories:[{category:"LISTEN",items:[{stableId:"kept"}]}],enrichment:{status:"FINALIZE",completedQueries:["done"],totalQueries:1,pendingQueries:0}}};
eeGetArtistCatalogue_=function(){return existing;};eeIncrementalResolvedEnrichment_=function(){return {readyForFinalization:true,categories:[{category:"LISTEN",items:[{stableId:"new-progress"}]}],enrichment:{status:"FINALIZE",completedQueries:["done","new"],totalQueries:2,pendingQueries:0}};};
eeGeneratePayloadLegacy_=function(){var error=new Error("APPLE_SEARCH_HTTP_429");error.code="APPLE_SEARCH_HTTP_429";error.retryable=true;throw error;};
eePutArtistCatalogue_=function(record){saved=record;};PropertiesService={getScriptProperties:function(){return {getProperty:function(key){return properties[key]||"";},setProperty:function(key,value){properties[key]=value;}};}};
var record=eeDiscoverArtistCatalogue_({slug:"artist",canonicalName:"Artist"},{id:"post"},true);
JSON.stringify({status:record.status,artistId:record.appleArtistId,confidence:record.identityConfidence,item:record.catalogue.categories[0].items[0].stableId,enrichment:record.enrichment.status,error:record.error,savedStatus:saved.status});
''')
        self.assertEqual(
            '{"status":"RESOLVED","artistId":"42","confidence":"HIGH","item":"new-progress",'
            '"enrichment":"FINALIZE_PENDING","error":"APPLE_SEARCH_HTTP_429","savedStatus":"RESOLVED"}',
            result,
        )

    def test_exhausted_artist_discovery_is_persisted_as_terminal_error(self):
        result = self.run_apps_script(r'''
var saved=null,properties={},nextLevel="LOW",nextArtistId=null;
eeAcquireWorkerLease_=function(){return true;};eeReleaseWorkerLease_=function(){};
eeGetArtistCatalogue_=function(){return {status:"UNRESOLVED"};};
eeGeneratePayloadLegacy_=function(){return {identity:{level:nextLevel,artistId:nextArtistId},categories:[{category:"LISTEN",items:[{stableId:"wrong",creator:"Other Artist"}]}]};};
eePutArtistCatalogue_=function(record){saved=record;};
PropertiesService={getScriptProperties:function(){return {getProperty:function(key){return properties[key]||"";},setProperty:function(key,value){properties[key]=value;}};}};
function attempt(level,artistId){nextLevel=level;nextArtistId=artistId;saved=null;var returned=eeDiscoverArtistCatalogue_({slug:"crimson-projekt",canonicalName:"Crimson ProjeKct"},{id:"post-1"},true);return {savedStatus:saved.status,savedConfidence:saved.identityConfidence,savedError:saved.error,savedCategories:saved.categories,returnedStatus:returned.status,returnedError:returned.error,catalogueCategories:returned.catalogue.categories};}
JSON.stringify({exhausted:attempt("LOW",null),plausible:attempt("MODERATE",null),confident:attempt("HIGH","123")});
''')
        self.assertEqual(
            '{"exhausted":{"savedStatus":"ERROR","savedConfidence":"LOW","savedError":"APPLE_ARTIST_DISCOVERY_EXHAUSTED",'
            '"savedCategories":[],"returnedStatus":"ERROR","returnedError":"APPLE_ARTIST_DISCOVERY_EXHAUSTED","catalogueCategories":[]},'
            '"plausible":{"savedStatus":"AMBIGUOUS","savedConfidence":"MODERATE","savedError":"","savedCategories":[],"returnedStatus":"AMBIGUOUS","returnedError":"","catalogueCategories":[]},'
            '"confident":{"savedStatus":"RESOLVED","savedConfidence":"HIGH","savedError":"","savedCategories":[],"returnedStatus":"RESOLVED","returnedError":"","catalogueCategories":[]}}',
            result,
        )

    def test_artist_discovery_cursor_advances_only_after_terminal_outcome(self):
        result = self.run_apps_script(r'''
function discoveryCase(rowStatus,failureAt,retryable){
  var props={EE_APPLE_ARTIST_DISCOVERY_INDEX:"1"},history=[],stored=[],fetches=0,discoveries=0;
  PropertiesService={getScriptProperties:function(){return {getProperty:function(key){return props[key]||"";},setProperty:function(key,value){props[key]=value;if(key==="EE_APPLE_ARTIST_DISCOVERY_INDEX")history.push(value);},deleteProperty:function(key){delete props[key];}};}};
  var row=["artist","Artist",1,1,"","","",rowStatus,"","","","post-1",""];
  eeArtistCatalogueSheet_=function(){return {getDataRange:function(){return {getValues:function(){return [["header"],row];}};}};};
  eeAcquireWorkerLease_=function(){return true;};eeReleaseWorkerLease_=function(){};
  eeSetExecutionDeadline_=function(value){EE_APPLE_EXECUTION_DEADLINE=value;};eeClearExecutionDeadline_=function(){EE_APPLE_EXECUTION_DEADLINE=0;};
  eeArtistRegistry_=function(){return {artists:[{slug:"artist",canonicalName:"Artist"}]};};
  eeFetchPostById_=function(){fetches+=1;if(failureAt==="fetch"){var error=new Error("FETCH_FAILED");error.code="FETCH_FAILED";error.retryable=retryable;throw error;}return {id:"post-1"};};
  eeDiscoverArtistCatalogue_=function(){discoveries+=1;if(failureAt==="discover"){var error=new Error("DISCOVERY_FAILED");error.code="DISCOVERY_FAILED";error.retryable=retryable;throw error;}stored.push("RESOLVED");return {status:"RESOLVED"};};
  eePutArtistCatalogue_=function(record){stored.push(record.status);};
  var workerResult=eeDiscoverArtistsWorker();
  return {status:workerResult.status,cursor:props.EE_APPLE_ARTIST_DISCOVERY_INDEX,history:history,stored:stored,fetches:fetches,discoveries:discoveries};
}
JSON.stringify({
  resolved:discoveryCase("RESOLVED","",false),
  success:discoveryCase("UNRESOLVED","",false),
  retryFetch:discoveryCase("UNRESOLVED","fetch",true),
  retryDiscovery:discoveryCase("UNRESOLVED","discover",true),
  fatalFetch:discoveryCase("UNRESOLVED","fetch",false)
});
''')
        self.assertEqual(
            '{"resolved":{"status":"OK","cursor":"2","history":["2"],"stored":[],"fetches":0,"discoveries":0},'
            '"success":{"status":"OK","cursor":"2","history":["1","2"],"stored":["RESOLVED"],"fetches":1,"discoveries":1},'
            '"retryFetch":{"status":"RETRY_LATER","cursor":"1","history":["1","1"],"stored":["UNRESOLVED"],"fetches":1,"discoveries":0},'
            '"retryDiscovery":{"status":"RETRY_LATER","cursor":"1","history":["1","1"],"stored":["UNRESOLVED"],"fetches":1,"discoveries":1},'
            '"fatalFetch":{"status":"OK","cursor":"2","history":["1","2"],"stored":["ERROR"],"fetches":1,"discoveries":0}}',
            result,
        )

    def test_retryable_artist_failures_pin_and_terminal_error_allows_later_rows(self):
        result = self.run_apps_script(r'''
function workerHarness(rows,discover){
  var props={EE_APPLE_ARTIST_DISCOVERY_INDEX:"1"},calls=[],stored=[];
  PropertiesService={getScriptProperties:function(){return {getProperty:function(key){return props[key]||"";},setProperty:function(key,value){props[key]=value;},deleteProperty:function(key){delete props[key];}};}};
  eeArtistCatalogueSheet_=function(){return {getDataRange:function(){return {getValues:function(){return [["header"]].concat(rows);}};}};};
  eeAcquireWorkerLease_=function(){return true;};eeReleaseWorkerLease_=function(){};
  eeSetExecutionDeadline_=function(value){EE_APPLE_EXECUTION_DEADLINE=value;};eeClearExecutionDeadline_=function(){EE_APPLE_EXECUTION_DEADLINE=0;};
  eeFetchPostById_=function(id){return {id:id};};
  eeArtistRegistry_=function(){return {artists:rows.map(function(row){return {slug:row[0],canonicalName:row[1]};})};};
  eeDiscoverArtistCatalogue_=function(artist,post){calls.push(artist.slug);return discover(artist,post);};
  eePutArtistCatalogue_=function(record){stored.push([record.artistKey,record.status,record.identityConfidence,record.error]);};
  var workerResult=eeDiscoverArtistsWorker();return {status:workerResult.status,cursor:props.EE_APPLE_ARTIST_DISCOVERY_INDEX,calls:calls,stored:stored};
}
function row(key){return [key,key,1,1,"","","","UNRESOLVED","","","","post-"+key,""];}
function transient(code){return workerHarness([row("first")],function(){var error=new Error(code);error.code=code;error.retryable=true;throw error;});}
var queue=workerHarness([row("dead-end"),row("later")],function(artist){return artist.slug==="dead-end"?{status:"ERROR",error:"APPLE_ARTIST_DISCOVERY_EXHAUSTED"}:{status:"RESOLVED"};});
JSON.stringify({http403:transient("APPLE_SEARCH_HTTP_403"),http429:transient("APPLE_SEARCH_HTTP_429"),headroom:transient("APPLE_SEARCH_EXECUTION_HEADROOM"),queue:queue});
''')
        self.assertEqual(
            '{"http403":{"status":"RETRY_LATER","cursor":"1","calls":["first"],"stored":[["first","UNRESOLVED","UNRESOLVED","APPLE_SEARCH_HTTP_403"]]},'
            '"http429":{"status":"RETRY_LATER","cursor":"1","calls":["first"],"stored":[["first","UNRESOLVED","UNRESOLVED","APPLE_SEARCH_HTTP_429"]]},'
            '"headroom":{"status":"RETRY_LATER","cursor":"1","calls":["first"],"stored":[["first","UNRESOLVED","UNRESOLVED","APPLE_SEARCH_EXECUTION_HEADROOM"]]},'
            '"queue":{"status":"OK","cursor":"3","calls":["dead-end","later"],"stored":[]}}',
            result,
        )

        worker = self.code[
            self.code.index("function eeDiscoverArtistsWorker") :
            self.code.index("function eeRefreshStaleArtistsWorker")
        ]
        for field in ("artistKey", "canonicalName", "terminalStatus", "errorReason", "nextCursor"):
            self.assertIn(field, worker)

    def test_stale_catalogues_have_an_independent_bounded_refresh_worker(self):
        worker = self.code[self.code.index("function eeRefreshStaleArtistsWorker") : self.code.index("function eeAssembleArticlePayloadsWorker")]
        self.assertIn("EE_APPLE_STALE_REFRESH_INDEX", worker)
        self.assertIn('eeDiscoverArtistCatalogue_(artist,post,isVerifiedResolved)', worker)
        self.assertIn('properties.setProperty("EE_APPLE_ASSEMBLY_INDEX","1")', worker)
        self.assertIn('status:"DEFERRED"', worker)
        self.assertIn('isVerifiedResolved?"ENRICHMENT_REFRESHED"', worker)
        self.assertIn('isDeferred?"DEFERRED_RETRIED":"IDENTITY_RETRIED"', worker)

    def test_legacy_stale_resolved_row_routes_to_resumable_enrichment(self):
        result = self.run_apps_script(r'''
var props={EE_APPLE_STALE_REFRESH_INDEX:"1"},forceValues=[];
var row=["lauryn-hill","Ms. Lauryn Hill",1,1,"99","mb","HIGH","RESOLVED",{categories:[{category:"LISTEN",items:[{stableId:"existing"}]}]},"","2000-01-01T00:00:00.000Z","post","",0,"",""];
PropertiesService={getScriptProperties:function(){return {getProperty:function(key){return props[key]||"";},setProperty:function(key,value){props[key]=value;},deleteProperty:function(key){delete props[key];}};}};
eeArtistCatalogueSheet_=function(){return {getDataRange:function(){return {getValues:function(){return [["header"],row];}};}};};eeAcquireWorkerLease_=function(){return true;};eeReleaseWorkerLease_=function(){};eeSetExecutionDeadline_=function(value){EE_APPLE_EXECUTION_DEADLINE=value;};eeClearExecutionDeadline_=function(){};
eeArtistRegistry_=function(){return {artists:[{slug:"lauryn-hill",canonicalName:"Ms. Lauryn Hill",ambiguityClass:"distinctive"}]};};eeFetchPostById_=function(){return {id:"post"};};
eeDiscoverArtistCatalogue_=function(artist,post,forceRefresh){forceValues.push(forceRefresh);return {status:"RESOLVED"};};
var worker=eeRefreshStaleArtistsWorker();JSON.stringify({status:worker.status,terminalStatus:worker.terminalStatus,forceValues:forceValues,cursor:props.EE_APPLE_STALE_REFRESH_INDEX,assembly:props.EE_APPLE_ASSEMBLY_INDEX});
''')
        self.assertEqual(
            '{"status":"ENRICHMENT_REFRESHED","terminalStatus":"RESOLVED",'
            '"forceValues":[true],"cursor":"2","assembly":"1"}',
            result,
        )

    def test_refresh_transport_failure_preserves_legacy_resolved_identity(self):
        result = self.run_apps_script(r'''
var props={EE_APPLE_STALE_REFRESH_INDEX:"1"},saved=null;
var oldCatalogue={categories:[{category:"LISTEN",items:[{stableId:"existing"}]}]};
var row=["maceo-parker","Maceo Parker",1,1,"42","mb","HIGH","RESOLVED",oldCatalogue,"","2000-01-01T00:00:00.000Z","post","",0,"",""];
PropertiesService={getScriptProperties:function(){return {getProperty:function(key){return props[key]||"";},setProperty:function(key,value){props[key]=value;},deleteProperty:function(key){delete props[key];}};}};
eeArtistCatalogueSheet_=function(){return {getDataRange:function(){return {getValues:function(){return [["header"],row];}};}};};eeAcquireWorkerLease_=function(){return true;};eeReleaseWorkerLease_=function(){};eeSetExecutionDeadline_=function(value){EE_APPLE_EXECUTION_DEADLINE=value;};eeClearExecutionDeadline_=function(){};
eeArtistRegistry_=function(){return {artists:[{slug:"maceo-parker",canonicalName:"Maceo Parker",ambiguityClass:"distinctive"}]};};eeFetchPostById_=function(){return {id:"post"};};eeDecodePayloadCell_=function(value){return value;};
eeDiscoverArtistCatalogue_=function(){var error=new Error("APPLE_SEARCH_EXECUTION_HEADROOM");error.code="APPLE_SEARCH_EXECUTION_HEADROOM";error.retryable=true;throw error;};eePutArtistCatalogue_=function(record){saved=record;};
var worker=eeRefreshStaleArtistsWorker();JSON.stringify({workerStatus:worker.status,terminalStatus:worker.terminalStatus,savedStatus:saved.status,artistId:saved.appleArtistId,confidence:saved.identityConfidence,item:saved.categories[0].items[0].stableId,enrichment:saved.enrichment.status,error:saved.error});
''')
        self.assertEqual(
            '{"workerStatus":"ENRICHMENT_PENDING","terminalStatus":"RESOLVED",'
            '"savedStatus":"RESOLVED","artistId":"42","confidence":"HIGH","item":"existing",'
            '"enrichment":"PENDING","error":"APPLE_SEARCH_EXECUTION_HEADROOM"}',
            result,
        )

    def test_clear_identity_transport_retry_is_short_and_ambiguous_identity_defers(self):
        result = self.run_apps_script(r'''
function identityCase(ambiguityClass){
  var props={EE_APPLE_ARTIST_DISCOVERY_INDEX:"1"},saved=null,row=["artist","Artist",1,1,"","","UNRESOLVED","UNRESOLVED","","","","post","",2,"",""];
  PropertiesService={getScriptProperties:function(){return {getProperty:function(key){return props[key]||"";},setProperty:function(key,value){props[key]=value;},deleteProperty:function(key){delete props[key];}};}};
  eeArtistCatalogueSheet_=function(){return {getDataRange:function(){return {getValues:function(){return [["header"],row];}};}};};eeAcquireWorkerLease_=function(){return true;};eeReleaseWorkerLease_=function(){};eeSetExecutionDeadline_=function(value){EE_APPLE_EXECUTION_DEADLINE=value;};eeClearExecutionDeadline_=function(){};eeFetchPostById_=function(){return {id:"post"};};
  eeArtistRegistry_=function(){return {artists:[{slug:"artist",canonicalName:"Artist",ambiguityClass:ambiguityClass}]};};eeDiscoverArtistCatalogue_=function(){var error=new Error("APPLE_SEARCH_HTTP_429");error.code="APPLE_SEARCH_HTTP_429";error.retryable=true;throw error;};eePutArtistCatalogue_=function(record){saved=record;};
  var worker=eeDiscoverArtistsWorker();return {worker:worker.status,status:saved.status,confidence:saved.identityConfidence,cursor:props.EE_APPLE_ARTIST_DISCOVERY_INDEX,retryMinutes:Math.round((Date.parse(saved.retryAfter)-Date.now())/60000)};
}
JSON.stringify({clear:identityCase("distinctive"),fish:identityCase("common_word")});
''')
        self.assertEqual(
            '{"clear":{"worker":"OK","status":"UNRESOLVED","confidence":"UNRESOLVED",'
            '"cursor":"2","retryMinutes":15},"fish":{"worker":"OK","status":"DEFERRED",'
            '"confidence":"DEFERRED","cursor":"2","retryMinutes":360}}',
            result,
        )

    def test_assembler_does_not_publish_empty_for_resolved_pending_catalogue(self):
        result = self.run_apps_script(r'''
var props={EE_APPLE_ASSEMBLY_INDEX:"1"},puts=[];
PropertiesService={getScriptProperties:function(){return {getProperty:function(key){return props[key]||"";},setProperty:function(key,value){props[key]=value;},deleteProperty:function(key){delete props[key];}};}};
eeAcquireWorkerLease_=function(){return true;};eeReleaseWorkerLease_=function(){};
eeArticleIdentitySheet_=function(){return {getDataRange:function(){return {getValues:function(){return [["header"],["post-1","",0,1,'["artist"]','["Artist"]',"HIGH",false,"","other"]];}};}};};
eeGetArtistCatalogue_=function(){return {status:"RESOLVED",catalogue:{categories:[],enrichment:{status:"PENDING",pendingQueries:2}}};};
eeFetchPostById_=function(){return {id:"post-1",title:"Artist",content:""};};eeAppleSettings_=function(){return {storefront:"FR"};};
eeGetPayload_=function(){return {categories:[{category:"LISTEN",items:[{stableId:"existing"}]}]};};
eePutPayload_=function(){puts.push([].slice.call(arguments));};
var result=eeAssembleArticlePayloadsWorker();JSON.stringify({status:result.status,processed:result.processed,puts:puts.length,cursor:props.EE_APPLE_ASSEMBLY_INDEX});
''')
        self.assertEqual(
            '{"status":"OK","processed":0,"puts":0,"cursor":"2"}',
            result,
        )

    def test_architecture_status_exposes_enrichment_counters(self):
        status_function = self.code[
            self.code.index("function eeArchitectureStatus") : self.code.index("function doGet")
        ]
        for counter in (
            "resolvedFullyEnriched",
            "resolvedEnrichmentPending",
            "partiallyEnrichedArtists",
            "articlesWaitingOnEnrichment",
            "unresolvedArtists",
            "deferredArtists",
        ):
            self.assertIn(counter, status_function)

    def test_architecture_counters_migrate_missing_enrichment_metadata_to_pending(self):
        result = self.run_apps_script(r'''
var logs=[];console.log=function(value){logs.push(value);};
var artists=[
 ["header"],
 ["full","Full",1,1,"1","","HIGH","RESOLVED",{categories:[{category:"LISTEN",items:[{stableId:"full"}]}],enrichment:{status:"FULL"}},"","2099-01-01T00:00:00.000Z","post-full","",0,"",""],
 ["legacy","Legacy",1,1,"2","","HIGH","RESOLVED",{categories:[{category:"LISTEN",items:[{stableId:"partial"}]}]},"","2000-01-01T00:00:00.000Z","post-legacy","",0,"",""],
 ["fish","Fish",1,1,"","","DEFERRED","DEFERRED",{categories:[]},"","","post-fish","",3,"","2099-01-01T00:00:00.000Z"]
];
var identities=[["header"],["post-legacy","",0,1,'["legacy"]']];
var payloads=[["header"]];
PropertiesService={getScriptProperties:function(){return {getProperty:function(){return "";}};}};
eeArticleIdentitySheet_=function(){return {getDataRange:function(){return {getValues:function(){return identities;}};}};};eeArtistCatalogueSheet_=function(){return {getDataRange:function(){return {getValues:function(){return artists;}};}};};eePayloadSheet_=function(){return {getDataRange:function(){return {getValues:function(){return payloads;}};}};};eeDecodePayloadCell_=function(value){return value;};
var status=eeArchitectureStatus();JSON.stringify({verified:status.verifiedAppleIds,full:status.resolvedFullyEnriched,pending:status.resolvedEnrichmentPending,partial:status.partiallyEnrichedArtists,stale:status.staleArtists,deferred:status.deferredArtists,waiting:status.articlesWaitingOnEnrichment});
''')
        self.assertEqual(
            '{"verified":2,"full":1,"pending":1,"partial":1,"stale":1,"deferred":1,"waiting":1}',
            result,
        )

    def test_bounded_transient_retries_defer_and_unblock_later_artist(self):
        result = self.run_apps_script(r'''
var props={EE_APPLE_ARTIST_DISCOVERY_INDEX:"1"},history=[],calls=[];
var rows=[
  ["blocked","Blocked",1,1,"","","","UNRESOLVED","","","","post-blocked","",0,"",""],
  ["later","Later",1,1,"","","","UNRESOLVED","","","","post-later","",0,"",""]
];
PropertiesService={getScriptProperties:function(){return {getProperty:function(key){return props[key]||"";},setProperty:function(key,value){props[key]=value;if(key==="EE_APPLE_ARTIST_DISCOVERY_INDEX")history.push(value);},deleteProperty:function(key){delete props[key];}};}};
eeArtistCatalogueSheet_=function(){return {getDataRange:function(){return {getValues:function(){return [["header"]].concat(rows);}};}};};
eeAcquireWorkerLease_=function(){return true;};eeReleaseWorkerLease_=function(){};
eeSetExecutionDeadline_=function(value){EE_APPLE_EXECUTION_DEADLINE=value;};eeClearExecutionDeadline_=function(){EE_APPLE_EXECUTION_DEADLINE=0;};
eeFetchPostById_=function(id){return {id:id};};
eeArtistRegistry_=function(){return {artists:[{slug:"blocked",canonicalName:"Blocked"},{slug:"later",canonicalName:"Later"}]};};
eePutArtistCatalogue_=function(record){var row=record.artistKey==="blocked"?rows[0]:rows[1];row[6]=record.identityConfidence;row[7]=record.status;row[12]=record.error;row[13]=record.transientRetryCount||0;row[14]=record.lastTransientError||"";row[15]=record.retryAfter||"";};
eeDiscoverArtistCatalogue_=function(artist){calls.push(artist.slug);if(artist.slug==="blocked"){var error=new Error("APPLE_SEARCH_HTTP_403");error.code="APPLE_SEARCH_HTTP_403";error.retryable=true;throw error;}rows[1][6]="HIGH";rows[1][7]="RESOLVED";return {status:"RESOLVED"};};
var first=eeDiscoverArtistsWorker(),firstState={status:first.status,cursor:props.EE_APPLE_ARTIST_DISCOVERY_INDEX,retries:rows[0][13],artistStatus:rows[0][7]};
var second=eeDiscoverArtistsWorker(),secondState={status:second.status,cursor:props.EE_APPLE_ARTIST_DISCOVERY_INDEX,retries:rows[0][13],artistStatus:rows[0][7]};
var third=eeDiscoverArtistsWorker(),thirdState={status:third.status,cursor:props.EE_APPLE_ARTIST_DISCOVERY_INDEX,retries:rows[0][13],artistStatus:rows[0][7],error:rows[0][12],retryAfter:!!rows[0][15],laterStatus:rows[1][7]};
JSON.stringify({first:firstState,second:secondState,third:thirdState,calls:calls,history:history});
''')
        self.assertEqual(
            '{"first":{"status":"RETRY_LATER","cursor":"1","retries":1,"artistStatus":"UNRESOLVED"},'
            '"second":{"status":"RETRY_LATER","cursor":"1","retries":2,"artistStatus":"UNRESOLVED"},'
            '"third":{"status":"OK","cursor":"3","retries":3,"artistStatus":"DEFERRED","error":"APPLE_SEARCH_HTTP_403","retryAfter":true,"laterStatus":"RESOLVED"},'
            '"calls":["blocked","blocked","blocked","later"],"history":["1","1","1","1","1","2","2","3"]}',
            result,
        )

    def test_all_retryable_artist_failures_are_bounded(self):
        result = self.run_apps_script(r'''
function bounded(code){
  var props={EE_APPLE_ARTIST_DISCOVERY_INDEX:"1"},row=["artist","Artist",1,1,"","","","UNRESOLVED","","","","post","",0,"",""];
  PropertiesService={getScriptProperties:function(){return {getProperty:function(k){return props[k]||"";},setProperty:function(k,v){props[k]=v;},deleteProperty:function(k){delete props[k];}};}};
  eeArtistCatalogueSheet_=function(){return {getDataRange:function(){return {getValues:function(){return [["header"],row];}};}};};eeAcquireWorkerLease_=function(){return true;};eeReleaseWorkerLease_=function(){};eeSetExecutionDeadline_=function(v){EE_APPLE_EXECUTION_DEADLINE=v;};eeClearExecutionDeadline_=function(){};eeFetchPostById_=function(){return {id:"post"};};eeArtistRegistry_=function(){return {artists:[{slug:"artist",canonicalName:"Artist"}]};};
  eePutArtistCatalogue_=function(record){row[6]=record.identityConfidence;row[7]=record.status;row[12]=record.error;row[13]=record.transientRetryCount||0;row[14]=record.lastTransientError||"";row[15]=record.retryAfter||"";};
  eeDiscoverArtistCatalogue_=function(){var e=new Error(code);e.code=code;e.retryable=true;throw e;};
  eeDiscoverArtistsWorker();eeDiscoverArtistsWorker();var final=eeDiscoverArtistsWorker();return [row[7],row[12],row[13],props.EE_APPLE_ARTIST_DISCOVERY_INDEX,final.status];
}
JSON.stringify({http429:bounded("APPLE_SEARCH_HTTP_429"),http504:bounded("APPLE_SEARCH_HTTP_504"),headroom:bounded("APPLE_SEARCH_EXECUTION_HEADROOM"),lease:bounded("ARTIST_DISCOVERY_BUSY")});
''')
        self.assertEqual(
            '{"http429":["DEFERRED","APPLE_SEARCH_HTTP_429",3,"2","OK"],'
            '"http504":["DEFERRED","APPLE_SEARCH_HTTP_504",3,"2","OK"],'
            '"headroom":["DEFERRED","APPLE_SEARCH_EXECUTION_HEADROOM",3,"2","OK"],'
            '"lease":["DEFERRED","ARTIST_DISCOVERY_BUSY",3,"2","OK"]}',
            result,
        )

    def test_deferred_artist_is_retried_after_cooldown_and_can_recover(self):
        result = self.run_apps_script(r'''
var props={EE_APPLE_STALE_REFRESH_INDEX:"1"},stored=[];
var row=["deferred","Deferred",1,1,"","","DEFERRED","DEFERRED","","","","post","APPLE_SEARCH_HTTP_403",3,"APPLE_SEARCH_HTTP_403","2000-01-01T00:00:00.000Z"];
PropertiesService={getScriptProperties:function(){return {getProperty:function(k){return props[k]||"";},setProperty:function(k,v){props[k]=v;},deleteProperty:function(k){delete props[k];}};}};
eeArtistCatalogueSheet_=function(){return {getDataRange:function(){return {getValues:function(){return [["header"],row];}};}};};eeAcquireWorkerLease_=function(){return true;};eeReleaseWorkerLease_=function(){};eeSetExecutionDeadline_=function(v){EE_APPLE_EXECUTION_DEADLINE=v;};eeClearExecutionDeadline_=function(){};eeFetchPostById_=function(){return {id:"post"};};eeArtistRegistry_=function(){return {artists:[{slug:"deferred",canonicalName:"Deferred"}]};};
eeDiscoverArtistCatalogue_=function(){row[6]="MODERATE";row[7]="AMBIGUOUS";row[12]="";row[13]=0;row[14]="";row[15]="";return {status:"AMBIGUOUS"};};
eePutArtistCatalogue_=function(record){stored.push(record);};
var worker=eeRefreshStaleArtistsWorker();JSON.stringify({result:worker,status:row[7],retries:row[13],cursor:props.EE_APPLE_STALE_REFRESH_INDEX});
''')
        self.assertEqual(
            '{"result":{"status":"DEFERRED_RETRIED","artistKey":"deferred","terminalStatus":"AMBIGUOUS","cursor":2},"status":"AMBIGUOUS","retries":0,"cursor":"2"}',
            result,
        )

    def test_stale_ready_and_empty_classifications(self):
        result = self.run_apps_script(r'''
JSON.stringify({
  stale:eePayloadHasRecommendations_({categories:[]}),
  ready:eePayloadHasRecommendations_({categories:[{category:"LISTEN",items:[{id:1}]}]}),
  noSubject:eeEmptyClassification_({primaryArtists:[]}),
  low:eeEmptyClassification_({primaryArtists:["Sparks"],identity:{level:"LOW"}}),
  noRaw:eeEmptyClassification_({primaryArtists:["Sparks"],identity:{level:"HIGH"},rawResultCount:0})
});
''')
        self.assertEqual('{"stale":false,"ready":true,"noSubject":"EMPTY_NO_SUBJECT","low":"EMPTY_IDENTITY_LOW","noRaw":"EMPTY_NO_RAW_RESULTS"}', result)

    def test_watch_requires_metadata_and_ranks_long_form_above_video(self):
        result = self.run_apps_script(r'''
var items=[],seen={};
eeAppleTvPush_(items,seen,{id:"title",title:"Sparks Fly",url:"https://tv.apple.com/movie/x/umc.cmc.title",description:"",cast:[]},"FR","Sparks");
eeAppleTvPush_(items,seen,{id:"doc",title:"The Sparks Brothers",url:"https://tv.apple.com/movie/x/umc.cmc.doc",description:"A documentary portrait of Sparks.",cast:[]},"FR","Sparks");
eeAppleTvPush_(items,seen,{id:"actor",title:"The Man Who Fell to Earth",url:"https://tv.apple.com/movie/x/umc.cmc.actor",description:"",cast:["David Bowie"]},"FR","David Bowie");
JSON.stringify(items.map(function(item){return [item.stableId,item.relevanceScore];}));
''')
        self.assertEqual('[["doc",99],["actor",97]]', result)
        self.assertIn('score=88;', self.code)

    def test_ambiguous_exact_artist_is_allowed_but_substring_watch_is_rejected(self):
        result = self.run_apps_script(r'''
var analysis={primaryArtists:["Yes"],people:[]};
var listen=eeCandidate_({collectionId:1,collectionName:"Fragile",artistName:"Yes",collectionViewUrl:"https://music.apple.com/a",artistId:10},{category:"LISTEN",entity:"album",term:"Yes",relationshipWeight:96,relationship:"primary band or artist",storefront:"FR"},analysis);
var watch=eeCandidate_({trackId:2,trackName:"Say Yes to Life",artistName:"Someone Else",trackViewUrl:"https://music.apple.com/v",description:""},{category:"WATCH",entity:"movie",term:"Yes",relationshipWeight:96,relationship:"primary band or artist",storefront:"FR"},analysis);
JSON.stringify({listen:!!listen,watch:!!watch});
''')
        self.assertEqual('{"listen":true,"watch":false}', result)

    def test_transient_retry_policy_403_429_503(self):
        result = self.run_apps_script(r'''
var stored={};
PropertiesService={getScriptProperties:function(){return {getProperty:function(k){return stored[k]||"";},setProperty:function(k,v){stored[k]=v;}};}};
LockService={getScriptLock:function(){return {waitLock:function(){},releaseLock:function(){}};}};
var sleeps=[];Utilities={sleep:function(ms){sleeps.push(ms);}};
function response(code){return {getResponseCode:function(){return code;},getContentText:function(){return "{}";}};}
var sequence=[403,200];UrlFetchApp={fetch:function(){return response(sequence.shift());}};
var recovered=eeAppleFetch_("https://itunes.apple.com/search",{},"APPLE_SEARCH").getResponseCode();
var classifications=[403,429,503].map(function(code){var error=eeAppleHttpError_("APPLE_SEARCH",code);return [error.code,error.retryable];});
sequence=[403,403,403];var failed="";try{eeAppleFetch_("https://itunes.apple.com/search",{},"APPLE_SEARCH");}catch(error){failed=error.code+":"+error.retryable;}
JSON.stringify({recovered:recovered,slept:sleeps.length>0,classifications:classifications,failed:failed});
''')
        self.assertIn('"recovered":200', result)
        self.assertIn('"APPLE_SEARCH_HTTP_403",true', result)
        self.assertIn('"APPLE_SEARCH_HTTP_429",true', result)
        self.assertIn('"APPLE_SEARCH_HTTP_503",true', result)
        self.assertIn('"failed":"APPLE_SEARCH_HTTP_403:true"', result)

    def test_more_than_24_items_survive_and_frontend_reveals_all(self):
        self.assertNotIn("categoryLimit", self.code)
        self.assertNotIn("maxPerCategory", self.theme)
        self.assertIn("var items=group.items.slice();", self.theme)
        self.assertIn("var next=Math.min(cards.length,visible+CONFIG.revealStep);", self.theme)
        self.assertIn('toggle.textContent=next>=cards.length?"Show less":"More";', self.theme)
        self.assertIn("card.hidden=index>=CONFIG.initialPerCategory;", self.theme)

        result = self.run_apps_script(r'''
eeAppleSettings_=function(){return {enabled:true,storefront:"FR"};};
eeArticleAnalysis_=function(){return {postId:"1",title:"Test Artist",primaryArtists:["Test Artist"],people:[],associatedPeople:[],existingAppleArtistIds:[],relationshipGraph:{nodes:[],edges:[]}};};
eeSearchPlan_=function(){return [{category:"LISTEN",media:"music",entity:"album",term:"Test Artist",intent:"ARTIST",relationship:"primary band or artist",relationshipWeight:96,storefront:"FR"}];};
eeAppleSearch_=function(){var rows=[];for(var i=1;i<=30;i+=1)rows.push({collectionId:i,collectionName:"Album "+i,artistName:"Test Artist",artistId:99,collectionViewUrl:"https://music.apple.com/album/"+i});return {results:rows};};
eePrimaryExactArtistIds_=function(){return [];};
eeResolveIdentity_=function(){return {level:"HIGH",artistId:"99",confidenceScore:100};};
eeAppleLookup_=function(){return {results:[]};};
eeAppleTvSearch_=function(){return [];};
var payload=eeGeneratePayloadLegacy_({id:"1",title:"Test Artist",content:"This Apple-free article discusses Test Artist.",labels:["Test Artist"],url:"https://example.test/post"});
JSON.stringify({ready:eePayloadHasRecommendations_(payload),count:payload.categories[0].items.length,version:payload.generationVersion});
''')
        self.assertEqual('{"ready":true,"count":30,"version":3}', result)

    def test_selective_refresh_has_independent_cursor_contract(self):
        refresh = self.code[self.code.index("function eeRefreshPayloadForPostId") :]
        self.assertNotIn('setProperty("EE_APPLE_BACKFILL_INDEX"', refresh)
        self.assertIn("EE_APPLE_REFRESH_READY_INDEX", refresh)
        self.assertIn("EE_APPLE_REFRESH_EMPTY_INDEX", refresh)
        self.assertIn("generationVersion: 3", self.code)

        result = self.run_apps_script(r'''
var stored={EE_APPLE_BACKFILL_INDEX:"77"};
PropertiesService={getScriptProperties:function(){return {getProperty:function(k){return stored[k]||"";},setProperty:function(k,v){stored[k]=v;},deleteProperty:function(k){delete stored[k];}};}};
eeFetchPostById_=function(id){return {id:id,title:"Selective",url:"",content:"",labels:[]};};
eeProcessPost_=function(post){return {generationVersion:2,postId:post.id,categories:[{category:"LISTEN",items:[{id:1}]}]};};
eeRefreshPayloadForPostId("3124541008960499514");
stored.EE_APPLE_BACKFILL_INDEX;
''')
        self.assertEqual("77", result)

    def test_fetch_post_by_id_pages_feed_returns_match_and_reports_exhaustion(self):
        helper = self.code[
            self.code.index("function eeFetchPostById_") :
            self.code.index("function eeRetryStoredErrors_")
        ]
        self.assertIn("eeFetchPosts_(startIndex, batchSize)", helper)
        self.assertIn("startIndex += posts.length", helper)
        self.assertNotIn("UrlFetchApp.fetch", helper)
        self.assertNotRegex(helper, r"EE_APPLE_CONFIG\.feedUrl\s*\+\s*[\"']/[\"']")
        self.assertIn('throw new Error("Blogger post not found: " + targetId)', helper)

        discovery_worker = self.code[
            self.code.index("function eeDiscoverArtistsWorker") :
            self.code.index("function eeRefreshStaleArtistsWorker")
        ]
        self.assertIn("eeFetchPostById_", discovery_worker)

        result = self.run_apps_script(r'''
var calls=[];
eeFetchPosts_=function(start,size){
  calls.push([start,size]);
  if(start===1)return [{id:"1"},{id:"2"}];
  if(start===3)return [{id:"999",title:"Target",url:"https://example.test/target",content:"Body",labels:["Target"]}];
  return [];
};
var post=eeFetchPostById_("999");
var foundCalls=calls.slice(),missing="";calls=[];
eeFetchPosts_=function(start,size){calls.push([start,size]);return start===1?[{id:"1"},{id:"2"}]:[];};
try{eeFetchPostById_("404");}catch(error){missing=error.message;}
JSON.stringify({id:post.id,title:post.title,foundCalls:foundCalls,missingCalls:calls,missing:missing});
''')
        self.assertEqual(
            '{"id":"999","title":"Target","foundCalls":[[1,500],[3,500]],'
            '"missingCalls":[[1,500],[3,500]],"missing":"Blogger post not found: 404"}',
            result,
        )

    def test_transient_failure_is_stored_as_error_and_batch_continues(self):
        result = self.run_apps_script(r'''
var writes=[];
eeAppleSettings_=function(){return {enabled:true};};
eeGeneratePayload_=function(){var error=new Error("APPLE_SEARCH_HTTP_403");error.retryable=true;throw error;};
eePutPayload_=function(post,payload,status,error){writes.push([post.id,status,error]);};
try{eeProcessPost_({id:"failed"});}catch(error){}
var props={EE_APPLE_BACKFILL_INDEX:"1"};
PropertiesService={getScriptProperties:function(){return {getProperty:function(k){return props[k]||"";},setProperty:function(k,v){props[k]=v;}};}};
eeFetchPosts_=function(){return [{id:"a",title:"A"},{id:"b",title:"B"}];};
eeGetPayload_=function(){return null;};
eeProcessPost_=function(post){if(post.id==="a")throw new Error("APPLE_SEARCH_HTTP_403");return {categories:[{category:"LISTEN",items:[{id:1}]}]};};
var batch=eeBackfillBatch(true);
JSON.stringify({write:writes[0],statuses:batch.results.map(function(item){return item.status;}),cursor:props.EE_APPLE_BACKFILL_INDEX});
''')
        self.assertEqual('{"write":["failed","ERROR","APPLE_SEARCH_HTTP_403"],"statuses":["ERROR","READY"],"cursor":"3"}', result)

    def test_retryable_backfill_failure_pins_cursor(self):
        result = self.run_apps_script(r'''
var props={EE_APPLE_BACKFILL_INDEX:"9"};
PropertiesService={getScriptProperties:function(){return {getProperty:function(k){return props[k]||"";},setProperty:function(k,v){props[k]=v;}};}};
eeAppleSettings_=function(){return {enabled:true};};
eeFetchPosts_=function(){return [{id:"a",title:"A"}];};eeGetPayload_=function(){return null;};
eeProcessPost_=function(){var error=new Error("APPLE_SEARCH_HTTP_429");error.code="APPLE_SEARCH_HTTP_429";error.retryable=true;throw error;};
var result=eeBackfillBatch(true);JSON.stringify({status:result.status,cursor:props.EE_APPLE_BACKFILL_INDEX,next:result.nextIndex});
''')
        self.assertEqual('{"status":"RETRY_LATER","cursor":"9","next":9}', result)

    def test_old_valid_ready_payload_remains_compatible(self):
        result = self.run_apps_script('JSON.stringify(eePayloadHasRecommendations_({schemaVersion:1,categories:[{category:"READ",items:[{stableId:"old"}]}]}));')
        self.assertEqual("true", result)

    def test_javascript_parses_with_system_javascript_compiler(self):
        scripts = {}
        for script_id in (
            "ee-safe-article-redesign-js",
            "ee-related-on-apple-candidate-js",
            "ee-apple-music-embed-enhancer",
        ):
            start = self.theme.index(f"<script id='{script_id}'")
            start = self.theme.index("//<![CDATA[", start) + len("//<![CDATA[")
            end = self.theme.index("//]]>", start)
            scripts[script_id] = self.theme[start:end]

        for script_id, source in scripts.items():
            check_javascript_syntax(source, script_id)
        check_javascript_syntax(self.code, "Code")


if __name__ == "__main__":
    unittest.main()
