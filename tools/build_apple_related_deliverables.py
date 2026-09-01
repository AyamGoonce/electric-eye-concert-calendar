"""Build production Apple-related deliverables from the supplied live exports."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables" / "apple-related"
THEME_SOURCE = ROOT / "sources" / "apple-related" / "Electric-Eye-Theme.base.xml"
CODE_SOURCE = ROOT / "sources" / "apple-related" / "Code.base.gs"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected one {label}, found {count}")
    return text.replace(old, new, 1)


def replace_function(text: str, name: str, next_name: str, replacement: str) -> str:
    start = text.index(f"function {name}(")
    end = text.index(f"function {next_name}(", start)
    return text[:start] + replacement.rstrip() + "\n\n" + text[end:]


def build_theme() -> str:
    theme = THEME_SOURCE.read_text(encoding="utf-8")
    theme = replace_once(
        theme,
        '    anchor.classList.add("ee-safe-affiliate-source");\n'
        '    anchor.hidden=true;\n'
        '    anchor.setAttribute("aria-hidden","true");\n\n'
        '    var sourceRow=anchor.closest(".separator");\n'
        '    if(sourceRow&&sourceRows.indexOf(sourceRow)===-1) sourceRows.push(sourceRow);',
        '    anchor.classList.add("ee-safe-affiliate-source");\n'
        '    anchor.setAttribute("data-ee-legacy-apple-source","true");\n'
        '    anchor.hidden=true;\n'
        '    anchor.setAttribute("aria-hidden","true");\n\n'
        '    var sourceRow=anchor.closest(".separator");\n'
        '    if(sourceRow&&sourceRows.indexOf(sourceRow)===-1){\n'
        '      sourceRow.setAttribute("data-ee-legacy-apple-row","true");\n'
        '      sourceRows.push(sourceRow);\n'
        '    }',
        "legacy source marker",
    )
    theme = replace_once(
        theme,
        '  function removeLegacySafeAffiliate(){\n'
        '    var modules=postBody.querySelectorAll(".ee-safe-affiliate:not(.ee-apple-generated)");\n'
        '    Array.prototype.forEach.call(modules,function(module){\n'
        '      var title=module.querySelector(".ee-safe-affiliate__title");\n'
        '      var relatedTitle=title&&norm(title.textContent)==="related on apple";\n'
        '      var relatedLabel=norm(module.getAttribute("aria-label"))==="related titles on apple";\n'
        '      if((relatedTitle||relatedLabel)&&module.querySelector(".ee-safe-affiliate__grid"))module.remove();\n'
        '    });\n'
        '  }',
        '  function isLegacyUtility(node){\n'
        '    if(!node||node.nodeType!==1)return false;\n'
        '    if(node.querySelector("img,iframe,video,audio,object,embed,form,table,ins.adsbygoogle"))return false;\n'
        '    var text=norm(node.textContent).replace(/:$/," ").trim();\n'
        '    return text==="sponsored content"||text==="sponsored item"||\n'
        '      text==="sponsored items"||text==="click here to subscribe to apple tv"||\n'
        '      text==="subscribe to apple tv"||text==="";\n'
        '  }\n'
        '  function removeAssociatedUtility(row,direction){\n'
        '    var node=row&&row[direction],guard=0;\n'
        '    while(node&&guard<6){\n'
        '      guard+=1;\n'
        '      if(node.nodeType===3&&norm(node.nodeValue)===""){node=node[direction];continue;}\n'
        '      if(node.nodeType===8){node=node[direction];continue;}\n'
        '      if(node.nodeType!==1||!isLegacyUtility(node))break;\n'
        '      var next=node[direction];node.remove();node=next;\n'
        '    }\n'
        '  }\n'
        '  function removeLegacySafeAffiliate(){\n'
        '    var modules=postBody.querySelectorAll(".ee-safe-affiliate:not(.ee-apple-generated)");\n'
        '    Array.prototype.forEach.call(modules,function(module){\n'
        '      var title=module.querySelector(".ee-safe-affiliate__title");\n'
        '      var relatedTitle=title&&norm(title.textContent)==="related on apple";\n'
        '      var relatedLabel=norm(module.getAttribute("aria-label"))==="related titles on apple";\n'
        '      if((relatedTitle||relatedLabel)&&module.querySelector(".ee-safe-affiliate__grid"))module.remove();\n'
        '    });\n'
        '    var rows=postBody.querySelectorAll("[data-ee-legacy-apple-row=true]");\n'
        '    Array.prototype.forEach.call(rows,function(row){\n'
        '      removeAssociatedUtility(row,"previousSibling");\n'
        '      removeAssociatedUtility(row,"nextSibling");\n'
        '      row.remove();\n'
        '    });\n'
        '    Array.prototype.forEach.call(postBody.querySelectorAll("[data-ee-legacy-apple-source=true]"),function(source){source.remove();});\n'
        '  }',
        "ready-payload legacy replacement",
    )
    theme = replace_once(
        theme,
        'var CONFIG={enabled:true,endpoint:"https://script.google.com/macros/s/AKfycbyxbAkw_Mcl_iXwV_N-JHS2rTf_KBwZlJKsD1RVECUlXR7WNXBt0eUAEIevZOiHXJpcaA/exec",callbackTimeout:15000,hoverDelay:200,initialPerCategory:4,revealStep:4,maxPerCategory:24};',
        'var CONFIG={enabled:true,endpoint:"https://script.google.com/macros/s/AKfycbyxbAkw_Mcl_iXwV_N-JHS2rTf_KBwZlJKsD1RVECUlXR7WNXBt0eUAEIevZOiHXJpcaA/exec",callbackTimeout:15000,hoverDelay:200,initialPerCategory:4,revealStep:4};',
        "frontend cap configuration",
    )
    theme = replace_once(
        theme,
        '      var items=group.items.slice(0,Math.min(CONFIG.maxPerCategory,24));',
        '      var items=group.items.slice();',
        "frontend item cap",
    )
    return theme


WORKER = r'''

/* Production archive worker. Configure one time-driven trigger manually. */
function eeBackfillWorker() {
  var settings=eeAppleSettings_();
  if(!settings.enabled)return {status:"DISABLED"};

  var started=Date.now(),safeStartCutoff=started+180000,iterations=0,stalled=0;
  var totals={ready:0,empty:0,error:0,skippedReady:0};
  var properties=PropertiesService.getScriptProperties();
  eeSetExecutionDeadline_(safeStartCutoff);

  while(Date.now()<safeStartCutoff){
    var before=Number(properties.getProperty("EE_APPLE_BACKFILL_INDEX")||1);
    var batch=eeBackfillBatch(true);
    iterations+=1;
    (batch.results||[]).forEach(function(item){
      if(item.status==="READY")totals.ready+=1;
      else if(item.status==="EMPTY")totals.empty+=1;
      else if(item.status==="ERROR")totals.error+=1;
      else if(item.status==="SKIPPED_READY")totals.skippedReady+=1;
    });

    if(batch.status==="RETRY_LATER")break;

    if(batch.status==="COMPLETE"){
      properties.setProperty("EE_APPLE_BACKFILL_COMPLETE","true");
      break;
    }
    var after=Number(properties.getProperty("EE_APPLE_BACKFILL_INDEX")||before);
    if(after<=before){
      stalled+=1;
      if(stalled>=2)break;
    }else stalled=0;
  }

  var retries=eeRetryStoredErrors_(safeStartCutoff);
  eeClearExecutionDeadline_();
  var result={
    status:Date.now()>=safeStartCutoff?"TIME_LIMIT":"OK",
    elapsedMs:Date.now()-started,
    iterations:iterations,
    totals:totals,
    retries:retries,
    cursor:Number(properties.getProperty("EE_APPLE_BACKFILL_INDEX")||1),
    primaryComplete:properties.getProperty("EE_APPLE_BACKFILL_COMPLETE")==="true",
    stalled:stalled
  };
  console.log(JSON.stringify(result));
  return result;
}

function eeFetchPostById_(postId) {
  var targetId = String(postId || "");
  var startIndex = 1;
  var batchSize = 500;

  while (true) {
    var posts = eeFetchPosts_(startIndex, batchSize);
    if (!posts.length) break;

    for (var i = 0; i < posts.length; i++) {
      if (String(posts[i].id) === targetId) return posts[i];
    }

    startIndex += posts.length;
  }

  throw new Error("Blogger post not found: " + targetId);
}

function eeRetryStoredErrors_(deadline) {
  if(PropertiesService.getScriptProperties().getProperty("EE_APPLE_BACKFILL_COMPLETE")!=="true")return {attempted:0,recovered:0,remaining:0};
  var sheet=eePayloadSheet_(),values=sheet.getDataRange().getValues();
  var attempted=0,recovered=0;
  for(var row=1;row<values.length&&Date.now()<deadline;row+=1){
    if(String(values[row][5])!=="ERROR")continue;
    var retryCount=Math.max(0,Number(values[row][7]||0));
    if(retryCount>=2)continue;
    attempted+=1;
    var postId=String(values[row][0]);
    try{
      var post=eeFetchPostById_(postId);
      var payload=eeProcessPost_(post,retryCount+1);
      if((payload.categories||[]).some(function(group){return (group.items||[]).length;}))recovered+=1;
    }catch(error){}
  }
  var current=sheet.getDataRange().getValues(),remaining=0;
  for(var index=1;index<current.length;index+=1)if(String(current[index][5])==="ERROR")remaining+=1;
  return {attempted:attempted,recovered:recovered,remaining:remaining};
}

function eeBackfillStatus() {
  var values=eePayloadSheet_().getDataRange().getValues();
  var counts={READY:0,EMPTY:0,ERROR:0},staleReady=0,latest="";
  for(var row=1;row<values.length;row+=1){
    var status=String(values[row][5]||"");
    if(status==="READY"&&!eeStoredPayloadHasRecommendations_(values[row][4]))staleReady+=1;
    else if(Object.prototype.hasOwnProperty.call(counts,status))counts[status]+=1;
    var generated=String(values[row][2]||"");
    if(generated>latest)latest=generated;
  }
  var properties=PropertiesService.getScriptProperties();
  var result={
    cursor:Number(properties.getProperty("EE_APPLE_BACKFILL_INDEX")||1),
    ready:counts.READY,
    empty:counts.EMPTY,
    error:counts.ERROR,
    staleReady:staleReady,
    totalStoredRows:Math.max(0,values.length-1),
    primaryComplete:properties.getProperty("EE_APPLE_BACKFILL_COMPLETE")==="true",
    mostRecentGeneratedAt:latest||null
  };
  console.log(JSON.stringify(result));
  return result;
}

function eeRefreshPayloadForPostId(postId) {
  postId=String(postId||"");
  if(!/^[0-9]+$/.test(postId))throw new Error("Numeric Blogger postId required");
  var properties=PropertiesService.getScriptProperties();
  eeSetExecutionDeadline_(Date.now()+180000);
  try{
    var post=eeFetchPostById_(postId);
    var payload=eeProcessPost_(post,0);
    return {postId:postId,status:eePayloadHasRecommendations_(payload)?"READY":"EMPTY",generationVersion:payload.generationVersion||1,categoryCounts:(payload.categories||[]).map(function(group){return [group.category,group.items.length];}),emptyClassification:(payload.diagnostics||{}).emptyClassification||null};
  }finally{eeClearExecutionDeadline_();}
}

function eeRefreshRowsWorker_(wantedStatus,cursorProperty) {
  var properties=PropertiesService.getScriptProperties(),started=Date.now(),cutoff=started+180000;
  eeSetExecutionDeadline_(cutoff);
  try{
    var values=eePayloadSheet_().getDataRange().getValues();
    var cursor=Math.max(1,Number(properties.getProperty(cursorProperty)||1)),processed=0,failed=0;
    for(var row=cursor;row<values.length&&Date.now()<cutoff;row+=1){
      properties.setProperty(cursorProperty,String(row+1));
      if(String(values[row][5])!==wantedStatus)continue;
      try{eeProcessPost_(eeFetchPostById_(String(values[row][0])),0);processed+=1;}catch(error){failed+=1;}
    }
    if(Number(properties.getProperty(cursorProperty)||1)>=values.length)properties.setProperty(cursorProperty,"1");
    var result={status:Date.now()>=cutoff?"TIME_LIMIT":"OK",wantedStatus:wantedStatus,processed:processed,failed:failed,cursor:Number(properties.getProperty(cursorProperty)||1)};
    console.log(JSON.stringify(result));return result;
  }finally{eeClearExecutionDeadline_();}
}

function eeRefreshReadyWorker() {return eeRefreshRowsWorker_("READY","EE_APPLE_REFRESH_READY_INDEX");}
function eeRefreshEmptyWorker() {return eeRefreshRowsWorker_("EMPTY","EE_APPLE_REFRESH_EMPTY_INDEX");}

function eeExplainPayloadForPostId(postId) {
  postId=String(postId||"");
  if(!/^[0-9]+$/.test(postId))throw new Error("Numeric Blogger postId required");
  var properties=PropertiesService.getScriptProperties();
  eeSetExecutionDeadline_(Date.now()+180000);
  try{
    var post=eeFetchPostById_(postId),payload=eeGeneratePayload_(post),diagnostics=payload.diagnostics||{};
    var result={title:post.title,primaryArtists:(payload.subject||{}).primaryArtists||[],people:(payload.subject||{}).people||[],identity:payload.identity||null,searchIntents:diagnostics.searchIntents||[],rawResultCount:diagnostics.rawResultCount||0,rejectedCount:diagnostics.rejectedCount||0,majorRejectionReasons:diagnostics.rejectionReasons||{},finalCategoryCounts:diagnostics.finalCategoryCounts||{},emptyClassification:diagnostics.emptyClassification||null};
    console.log(JSON.stringify(result));return result;
  }finally{eeClearExecutionDeadline_();}
}
'''


APPLE_REQUESTS = r'''
var EE_APPLE_EXECUTION_DEADLINE=0;
function eeSetExecutionDeadline_(value){EE_APPLE_EXECUTION_DEADLINE=Number(value||0);}
function eeClearExecutionDeadline_(){EE_APPLE_EXECUTION_DEADLINE=0;}

function eeAppleTransientCode_(code) {
  return [403,429,500,502,503,504].indexOf(Number(code))!==-1;
}

function eeAppleHttpError_(label, code) {
  var error=new Error(String(label||"APPLE_SEARCH")+"_HTTP_"+String(code));
  error.code=String(label||"APPLE_SEARCH")+"_HTTP_"+String(code);
  error.retryable=eeAppleTransientCode_(code);
  return error;
}

function eeAppleFetch_(url, options, label) {
  var lock=LockService.getScriptLock();
  lock.waitLock(30000);
  try{
    var properties=PropertiesService.getScriptProperties();
    var deadline=EE_APPLE_EXECUTION_DEADLINE;
    var cooldown=Number(properties.getProperty("EE_APPLE_COOLDOWN_UNTIL")||0);
    if(cooldown>Date.now()){var cooling=new Error("APPLE_RETRY_LATER_COOLDOWN");cooling.code="APPLE_RETRY_LATER_COOLDOWN";cooling.retryable=true;throw cooling;}
    var attempts=3,lastError=null;
    for(var attempt=0;attempt<attempts;attempt+=1){
      var last=Number(properties.getProperty("EE_APPLE_LAST_REQUEST_AT")||0);
      var throttleWait=Math.max(0,EE_APPLE_CONFIG.minimumRequestIntervalMs-(Date.now()-last));
      var backoff=attempt?Math.pow(2,attempt-1)*1200+Math.floor(Math.random()*350):0;
      var wait=Math.max(throttleWait,backoff);
      if(deadline&&Date.now()+wait+15000>=deadline){
        var headroom=new Error("APPLE_SEARCH_EXECUTION_HEADROOM");
        headroom.code="APPLE_SEARCH_EXECUTION_HEADROOM";
        headroom.retryable=true;
        throw headroom;
      }
      if(wait)Utilities.sleep(wait);
      var response=UrlFetchApp.fetch(url,options);
      properties.setProperty("EE_APPLE_CALL_COUNT",String(Number(properties.getProperty("EE_APPLE_CALL_COUNT")||0)+1));
      properties.setProperty("EE_APPLE_LAST_REQUEST_AT",String(Date.now()));
      var code=response.getResponseCode();
      if(code===200)return response;
      lastError=eeAppleHttpError_(label,code);
      if(!lastError.retryable)throw lastError;
      properties.setProperty("EE_APPLE_LAST_TRANSIENT_FAILURE",new Date().toISOString()+" "+lastError.code);
    }
    if(lastError&&lastError.retryable)properties.setProperty("EE_APPLE_COOLDOWN_UNTIL",String(Date.now()+300000));
    throw lastError||new Error(String(label||"APPLE_SEARCH")+"_FAILED");
  }finally{
    lock.releaseLock();
  }
}

function eeAppleSearch_(query) {
  var params={term:query.term,country:String(query.storefront||EE_APPLE_CONFIG.storefront).toLowerCase(),media:query.media,entity:query.entity,limit:Math.min(EE_APPLE_CONFIG.searchLimit,200),lang:"fr_fr",explicit:"Yes"};
  var queryString=Object.keys(params).map(function(key){return encodeURIComponent(key)+"="+encodeURIComponent(params[key]);}).join("&");
  var url="https://itunes.apple.com/search?"+queryString;
  var digest=Utilities.base64EncodeWebSafe(Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256,url)).slice(0,40);
  var cache=CacheService.getScriptCache(),cacheKey="apple-search:"+digest,cached=cache.get(cacheKey);
  if(cached){var properties=PropertiesService.getScriptProperties();properties.setProperty("EE_APPLE_CACHE_HIT_COUNT",String(Number(properties.getProperty("EE_APPLE_CACHE_HIT_COUNT")||0)+1));return JSON.parse(cached);}
  var response=eeAppleFetch_(url,{muteHttpExceptions:true,headers:{Accept:"application/json"}},"APPLE_SEARCH");
  var value=JSON.parse(response.getContentText()),cacheText=JSON.stringify(value);
  if(cacheText.length<95000)cache.put(cacheKey,cacheText,EE_APPLE_CONFIG.payloadCacheSeconds);
  return value;
}

function eeAppleLookup_(query) {
  var ids=eeUnique_((query.ids||[]).map(String).filter(Boolean)).slice(0,200);
  if(!ids.length)return {resultCount:0,results:[]};
  var params={id:ids.join(","),country:String(query.storefront||EE_APPLE_CONFIG.storefront).toLowerCase(),entity:query.entity||"",limit:Math.min(EE_APPLE_CONFIG.searchLimit,200)};
  var queryString=Object.keys(params).filter(function(key){return params[key]!=="";}).map(function(key){return encodeURIComponent(key)+"="+encodeURIComponent(params[key]);}).join("&");
  var url="https://itunes.apple.com/lookup?"+queryString;
  var digest=Utilities.base64EncodeWebSafe(Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256,url)).slice(0,40);
  var cache=CacheService.getScriptCache(),cacheKey="apple-lookup:"+digest,cached=cache.get(cacheKey);
  if(cached){var properties=PropertiesService.getScriptProperties();properties.setProperty("EE_APPLE_CACHE_HIT_COUNT",String(Number(properties.getProperty("EE_APPLE_CACHE_HIT_COUNT")||0)+1));return JSON.parse(cached);}
  var response=eeAppleFetch_(url,{muteHttpExceptions:true,headers:{Accept:"application/json"}},"APPLE_LOOKUP");
  var value=JSON.parse(response.getContentText()),cacheText=JSON.stringify(value);
  if(cacheText.length<95000)cache.put(cacheKey,cacheText,EE_APPLE_CONFIG.payloadCacheSeconds);
  return value;
}
'''


QUALITY_HELPERS = r'''
function eePayloadHasRecommendations_(payload) {
  return !!(payload&&Array.isArray(payload.categories)&&payload.categories.some(function(group){
    return group&&Array.isArray(group.items)&&group.items.length>0;
  }));
}

function eeStoredPayloadHasRecommendations_(stored) {
  var value=String(stored||"");
  if(value.indexOf("GZIP64:")===0)return true;
  try{return eePayloadHasRecommendations_(JSON.parse(value));}catch(error){return false;}
}

function eeReviewedPostSubjects_(postId) {
  try{var override=(eeArtistRegistry_().articleOverrides||{})[String(postId||"")]||{};return override.primaryArtists||[];}catch(error){return [];}
}

function eeEmptyClassification_(diagnostics) {
  diagnostics=diagnostics||{};
  if(!diagnostics.primaryArtists||!diagnostics.primaryArtists.length)return "EMPTY_NO_SUBJECT";
  if(!diagnostics.identity||diagnostics.identity.level!=="HIGH")return "EMPTY_IDENTITY_LOW";
  if(!Number(diagnostics.rawResultCount||0))return "EMPTY_NO_RAW_RESULTS";
  if(Number(diagnostics.acceptedCount||0)===0&&Number(diagnostics.rejectedCount||0)>0)return "EMPTY_ALL_CANDIDATES_REJECTED";
  if(Number(diagnostics.relationshipRejectedCount||0)>0)return "EMPTY_NO_QUALIFYING_RELATIONSHIP";
  return "EMPTY_OTHER";
}

function eePublicPayload_(payload) {
  if(!payload)return null;
  var copy=JSON.parse(JSON.stringify(payload));
  delete copy.diagnostics;
  return copy;
}
'''


APPLE_TV_PUSH = r'''
function eeAppleTvPush_(items, seen, raw, storefront, subject) {
  var id=String(raw.id||""),title=String(raw.title||"").trim(),url=String(raw.url||"").trim();
  if(!id||!title||!url||seen[id]||!subject)return;
  var description=String(raw.description||"").replace(/<[^>]+>/g," ").replace(/\s+/g," ").trim();
  var cast=eeUnique_([].concat(raw.cast||[]).concat(raw.performers||[]));
  var credits=eeUnique_([].concat(raw.directors||[]).concat(raw.credits||[]));
  var subjectNorm=eeNorm_(subject);
  var castMatch=cast.concat(credits).some(function(name){return eeNorm_(name)===subjectNorm;});
  var metadata=[description,cast.join(" "),credits.join(" ")].join(" ");
  var subjectMetadata=eeContains_(metadata,subject);
  var longForm=/documentary|documentaire|concert film|live concert|concert movie|portrait|biograph/i.test([title,description].join(" "));
  if(!castMatch&&!(subjectMetadata&&longForm))return;
  seen[id]=true;
  var score=subjectMetadata&&longForm?99:97;
  var reason=subjectMetadata&&longForm?"Apple metadata identifies a substantial film about the article artist.":"Apple cast or credits identify the article artist.";
  items.push({stableId:id,title:title,canonicalAppleUrl:url,url:eeAffiliateUrl_("WATCH",url),artworkUrl:String(raw.artworkUrl||""),creator:"",mediaType:String(raw.mediaType||"Film"),description:description,cast:cast,director:credits.join(", "),storefront:String(storefront||"FR").toUpperCase(),category:"WATCH",relevanceTier:"DIRECT",relevanceScore:score,relevanceReason:reason,relationshipContext:reason,price:null,discoverySource:"APPLE_TV_PUBLIC_SEARCH"});
}
'''


ARTIST_REGISTRY = r'''
function eeArtistRegistry_() {
  var cache=CacheService.getScriptCache(),key="ee-artist-registry-v1",cached=cache.get(key);
  if(cached)return JSON.parse(cached);
  var response=UrlFetchApp.fetch(EE_APPLE_CONFIG.artistIndexUrl,{muteHttpExceptions:true,headers:{Accept:"application/json"}});
  if(response.getResponseCode()!==200)throw new Error("ARTIST_REGISTRY_HTTP_"+response.getResponseCode());
  var registry=JSON.parse(response.getContentText());
  if(registry.schemaVersion!==1||!Array.isArray(registry.artists))throw new Error("ARTIST_REGISTRY_SCHEMA");
  var text=JSON.stringify(registry);if(text.length<95000)cache.put(key,text,21600);
  return registry;
}

function eeExactEntityInText_(text,name) {return eeContains_(text,name);}

function eeFastArticleIdentity_(post, registry) {
  registry=registry||eeArtistRegistry_();
  var postId=String(post.id||""),override=(registry.articleOverrides||{})[postId]||null;
  var labels=(post.labels||[]).map(function(value){return String(value||"").trim();});
  var normalizedLabels={};labels.forEach(function(value){normalizedLabels[eeNorm_(value)]=true;});
  var structuralLabels={};(registry.structuralLabels||[]).forEach(function(value){structuralLabels[eeNorm_(value)]=true;});
  var title=String(post.title||""),body=String(post.content||"").replace(/<[^>]+>/g," ").replace(/&nbsp;|&#160;/gi," ");
  var matches=[];
  function evidenceFor(artist){
    var names=eeUnique_([artist.canonicalName].concat(artist.aliases||[]).concat(artist.alternateSpellings||[]));
    var exactLabel=names.some(function(name){var key=eeNorm_(name);return normalizedLabels[key]&&!structuralLabels[key];});
    var titleMatch=names.some(function(name){return eeExactEntityInText_(title,name);});
    var articleKnown=(artist.articleIds||[]).map(String).indexOf(postId)!==-1;
    var relationshipTerms=[]
      .concat(artist.members||[],artist.formerMembers||[],artist.associatedActs||[],artist.sideProjects||[],artist.keywords||[]);
    var relationshipHits=relationshipTerms.filter(function(name){return eeExactEntityInText_(title+" "+body,name);});
    var mentions=names.reduce(function(total,name){var needle=eeNorm_(name),hay=eeNorm_(body);return total+(needle?hay.split(needle).length-1:0);},0);
    var ambiguous=artist.ambiguityClass&&artist.ambiguityClass!=="distinctive";
    var accepted=articleKnown||(!ambiguous&&(exactLabel||titleMatch))||(ambiguous&&exactLabel&&(relationshipHits.length>0||mentions>=2));
    return {accepted:accepted,score:articleKnown?120:exactLabel&&relationshipHits.length?110:exactLabel&&mentions>=2?105:exactLabel?96:titleMatch?88:0,evidence:[articleKnown&&"existing artist-index article association",exactLabel&&"exact Blogger artist label",titleMatch&&"bounded title identity",relationshipHits.length&&("relationship corroboration: "+relationshipHits.join(", ")),mentions>=2&&"repeated body mentions"].filter(Boolean),ambiguous:ambiguous};
  }
  if(override){
    (override.primaryArtists||[]).forEach(function(name){var artist=(registry.artists||[]).filter(function(value){return eeNorm_(value.canonicalName)===eeNorm_(name);})[0];if(artist)matches.push({artist:artist,score:130,evidence:override.identityEvidence||["reviewed article override"],ambiguous:false});});
  }else{
    (registry.artists||[]).forEach(function(artist){var result=evidenceFor(artist);if(result.accepted)matches.push({artist:artist,score:result.score,evidence:result.evidence,ambiguous:result.ambiguous});});
  }
  if(!matches.length&&!override){
    var candidate="",concert=title.match(/^(.+?)\s+@\s+/),action=title.match(/^(.+?)\s+(?:announce|announces|release|releases|share|shares|unveil|unveils|return|returns|perform|performs)\b/i),album=title.match(/^album review\s*:\s*(.+?)(?:\s+[–-]\s+|$)/i);
    candidate=String((concert||action||album||[])[1]||"").trim();
    var candidateNorm=eeNorm_(candidate),generic=/^(?:news|review|music|concert|festival|tour|video|album|single|song|track|show|tickets?|paris|new)$/i,ambiguousWords={beat:true,down:true,possessed:true,live:true,ghost:true,tool:true,kiss:true,sparks:true};
    var corroborated=labels.some(function(label){return eeNorm_(label)===candidateNorm;});
    if(candidate&&corroborated&&!generic.test(candidate)&&!ambiguousWords[candidateNorm])matches.push({artist:{canonicalName:candidate,slug:candidateNorm.replace(/\s+/g,"-"),aliases:[],articleIds:[],ambiguityClass:"provisional"},score:94,evidence:["provisional exact title and Blogger label"],ambiguous:false});
  }
  matches.sort(function(a,b){return b.score-a.score||a.artist.canonicalName.localeCompare(b.artist.canonicalName);});
  var articleType=/playlist/i.test(title)||labels.some(function(label){return /playlist/i.test(label);})?"playlist":/obituary|r\.i\.p\./i.test(title)?"obituary":/interview/i.test(title)?"interview":/@/.test(title)?"concert_review":/album review/i.test(title)?"album_review":"other";
  return {schemaVersion:1,analysisVersion:1,postId:postId,canonicalUrl:post.url||"",primaryArtistKeys:matches.map(function(item){return item.artist.slug;}),primaryArtists:matches.map(function(item){return item.artist.canonicalName;}),people:[],identityConfidence:matches.length?(matches[0].score>=105?"HIGH":"MEDIUM"):"NONE",identityEvidence:matches.map(function(item){return {artistKey:item.artist.slug,evidence:item.evidence};}),ambiguous:matches.some(function(item){return item.ambiguous;}),articleType:articleType};
}

function eeNamedSheet_(name,header) {
  var settings=eeAppleSettings_();if(!settings.spreadsheetId)throw new Error("EE_APPLE_SPREADSHEET_ID is not configured");
  var spreadsheet=SpreadsheetApp.openById(settings.spreadsheetId),sheet=spreadsheet.getSheetByName(name)||spreadsheet.insertSheet(name);
  if(sheet.getLastRow()===0)sheet.appendRow(header);
  return sheet;
}

function eeAcquireWorkerLease_(name,ttlMs) {
  var lock=LockService.getScriptLock();lock.waitLock(30000);
  try{var properties=PropertiesService.getScriptProperties(),key="EE_APPLE_LEASE_"+name,until=Number(properties.getProperty(key)||0);if(until>Date.now())return false;properties.setProperty(key,String(Date.now()+ttlMs));return true;}finally{lock.releaseLock();}
}
function eeReleaseWorkerLease_(name) {var lock=LockService.getScriptLock();lock.waitLock(30000);try{PropertiesService.getScriptProperties().deleteProperty("EE_APPLE_LEASE_"+name);}finally{lock.releaseLock();}}

function eeArticleIdentitySheet_() {return eeNamedSheet_("Apple Article Identity",["postId","canonicalUrl","analyzedAt","analysisVersion","primaryArtistKeys","primaryArtists","confidence","ambiguous","evidenceJson","articleType"]);}
function eeArtistCatalogueSheet_() {return eeNamedSheet_("Apple Artists",["artistKey","canonicalName","registrySchemaVersion","catalogueSchemaVersion","appleArtistId","musicBrainzId","identityConfidence","status","catalogueJson","generatedAt","staleAfter","representativePostId","error"]);}

function eeUpsertRow_(sheet,key,value,rowValues) {
  var values=sheet.getDataRange().getValues(),target=values.length+1;
  for(var row=1;row<values.length;row+=1)if(String(values[row][key])===String(value)){target=row+1;break;}
  sheet.getRange(target,1,1,rowValues.length).setValues([rowValues]);return target;
}

function eePutArticleIdentity_(analysis, registry, knownArtistKeys) {
  var sheet=eeArticleIdentitySheet_();
  eeUpsertRow_(sheet,0,analysis.postId,[analysis.postId,analysis.canonicalUrl,new Date().toISOString(),analysis.analysisVersion,JSON.stringify(analysis.primaryArtistKeys),JSON.stringify(analysis.primaryArtists),analysis.identityConfidence,String(analysis.ambiguous),JSON.stringify(analysis.identityEvidence),analysis.articleType]);
  registry=registry||eeArtistRegistry_();knownArtistKeys=knownArtistKeys||null;
  analysis.primaryArtistKeys.forEach(function(key,index){var artist=registry.artists.filter(function(value){return value.slug===key;})[0]||{canonicalName:analysis.primaryArtists[index],slug:key};if(knownArtistKeys&&knownArtistKeys[key])return;var existing=knownArtistKeys?null:eeGetArtistCatalogue_(key);if(existing)return;eePutArtistCatalogue_({artistKey:key,canonicalName:artist.canonicalName,status:"UNRESOLVED",representativePostId:analysis.postId,identityConfidence:"UNRESOLVED",categories:[]});if(knownArtistKeys)knownArtistKeys[key]=true;});
}

function eeGetArtistCatalogue_(artistKey) {
  var values=eeArtistCatalogueSheet_().getDataRange().getValues();
  for(var row=1;row<values.length;row+=1)if(String(values[row][0])===String(artistKey)){var payload=String(values[row][8]||""),staleAfter=String(values[row][10]||"");return {artistKey:String(values[row][0]),canonicalName:String(values[row][1]),appleArtistId:String(values[row][4]||""),musicBrainzId:String(values[row][5]||""),identityConfidence:String(values[row][6]||""),status:String(values[row][7]||""),catalogue:payload?eeDecodePayloadCell_(payload):null,generatedAt:String(values[row][9]||""),staleAfter:staleAfter,isStale:!!staleAfter&&Date.parse(staleAfter)<=Date.now(),representativePostId:String(values[row][11]||""),error:String(values[row][12]||"")};}
  return null;
}

function eePutArtistCatalogue_(record) {
  var sheet=eeArtistCatalogueSheet_(),now=new Date(),generated=record.generatedAt||now.toISOString(),stale=record.staleAfter||new Date(now.getTime()+30*86400000).toISOString();
  var catalogue={schemaVersion:1,generationVersion:EE_APPLE_CONFIG.generationVersion,artistKey:record.artistKey,canonicalName:record.canonicalName,categories:record.categories||[]};
  eeUpsertRow_(sheet,0,record.artistKey,[record.artistKey,record.canonicalName,1,1,record.appleArtistId||"",record.musicBrainzId||"",record.identityConfidence||"",record.status||"UNRESOLVED",eeEncodePayloadCell_(catalogue),generated,stale,record.representativePostId||"",record.error||""]);
}

function eeAssemblePayloadFromCatalogues_(post,analysis,catalogues) {
  var groups={LISTEN:{},WATCH:{},READ:{}},articleText=String(post.title||"")+" "+String(post.content||"").replace(/<[^>]+>/g," ");
  catalogues.forEach(function(record){((record.catalogue||{}).categories||[]).forEach(function(group){(group.items||[]).forEach(function(item){var ranked=JSON.parse(JSON.stringify(item)),boost=0;if(ranked.title&&eeExactEntityInText_(articleText,ranked.title))boost+=6;if(analysis.articleType==="interview"&&ranked.creator&&eeExactEntityInText_(post.title||"",ranked.creator))boost+=3;ranked.relevanceScore=Number(ranked.relevanceScore||0)+boost;var key=String(ranked.stableId||ranked.url||ranked.title),existing=groups[group.category]&&groups[group.category][key];if(groups[group.category]&&(!existing||Number(ranked.relevanceScore||0)>Number(existing.relevanceScore||0)))groups[group.category][key]=ranked;});});});
  var categories=[];["LISTEN","WATCH","READ"].forEach(function(category){var items=Object.keys(groups[category]).map(function(key){return groups[category][key];});items.sort(function(a,b){return Number(b.relevanceScore||0)-Number(a.relevanceScore||0)||String(a.title).localeCompare(String(b.title));});if(items.length)categories.push({category:category,items:items});});
  return {schemaVersion:1,generationVersion:EE_APPLE_CONFIG.generationVersion,generatedAt:new Date().toISOString(),postId:String(post.id),canonicalUrl:post.url||"",storefront:eeAppleSettings_().storefront,subject:{title:post.title||"",primaryArtists:analysis.primaryArtists,people:analysis.people||[]},identity:{level:analysis.identityConfidence,artistId:catalogues.length===1?catalogues[0].appleArtistId||null:null,confidenceScore:analysis.identityConfidence==="HIGH"?100:75},categories:categories,diagnostics:{architecture:"ARTIST_REGISTRY_V1",artistKeys:analysis.primaryArtistKeys,cacheHits:catalogues.length,emptyClassification:categories.length?null:(analysis.primaryArtistKeys.length?"EMPTY_NO_QUALIFYING_RELATIONSHIP":"EMPTY_NO_SUBJECT")}};
}

function eeDiscoverArtistCatalogue_(artist,post,forceRefresh) {
  var lease="CATALOGUE_"+String(artist.slug||"").replace(/[^A-Za-z0-9_-]/g,"_");
  if(!eeAcquireWorkerLease_(lease,360000)){var busy=new Error("ARTIST_DISCOVERY_BUSY");busy.code="ARTIST_DISCOVERY_BUSY";busy.retryable=true;throw busy;}
  try{
    var existing=eeGetArtistCatalogue_(artist.slug);if(existing&&existing.status!=="UNRESOLVED"&&!forceRefresh)return existing;
    var legacy=eeGeneratePayloadLegacy_(post),identity=legacy.identity||{};
    var categories=(legacy.categories||[]).map(function(group){return {category:group.category,items:(group.items||[]).filter(function(item){return !item.creator||eeNorm_(item.creator)===eeNorm_(artist.canonicalName)||group.category!=="LISTEN";})};}).filter(function(group){return group.items.length;});
    var confidence=String(identity.level||"LOW"),appleArtistId=identity.artistId||artist.appleArtistId||"",status=(appleArtistId||confidence==="HIGH")?"RESOLVED":confidence==="MODERATE"?"AMBIGUOUS":"ERROR",errorReason=status==="ERROR"?"APPLE_ARTIST_DISCOVERY_EXHAUSTED":"";
    if(status==="ERROR")categories=[];
    var record={artistKey:artist.slug,canonicalName:artist.canonicalName,appleArtistId:appleArtistId,musicBrainzId:artist.musicBrainzId||"",identityConfidence:confidence,status:status,error:errorReason,categories:categories,representativePostId:String(post.id)};
    eePutArtistCatalogue_(record);var properties=PropertiesService.getScriptProperties();properties.setProperty("EE_APPLE_CATALOGUE_GENERATION_COUNT",String(Number(properties.getProperty("EE_APPLE_CATALOGUE_GENERATION_COUNT")||0)+1));record.catalogue={schemaVersion:1,generationVersion:EE_APPLE_CONFIG.generationVersion,artistKey:record.artistKey,canonicalName:record.canonicalName,categories:record.categories};return record;
  }finally{eeReleaseWorkerLease_(lease);}
}

function eeGeneratePayload_(post) {
  var registry=eeArtistRegistry_(),analysis=eeFastArticleIdentity_(post,registry);eePutArticleIdentity_(analysis);
  if(!analysis.primaryArtistKeys.length)return eeAssemblePayloadFromCatalogues_(post,analysis,[]);
  var catalogues=[];
  analysis.primaryArtistKeys.forEach(function(key,index){var artist=registry.artists.filter(function(value){return value.slug===key;})[0]||{canonicalName:analysis.primaryArtists[index],slug:key,aliases:[],ambiguityClass:"provisional"},record=eeGetArtistCatalogue_(key);if(!record||record.status==="UNRESOLVED")record=eeDiscoverArtistCatalogue_(artist,post);if(record&&record.status==="RESOLVED")catalogues.push(record);});
  return eeAssemblePayloadFromCatalogues_(post,analysis,catalogues);
}

function eeAnalyzeArchiveWorker() {
  if(!eeAcquireWorkerLease_("IDENTITY",240000))return {status:"BUSY"};
  try{var properties=PropertiesService.getScriptProperties(),cursor=Math.max(1,Number(properties.getProperty("EE_APPLE_IDENTITY_INDEX")||1)),posts=eeFetchPosts_(cursor,100),registry=eeArtistRegistry_(),artistRows=eeArtistCatalogueSheet_().getDataRange().getValues(),knownArtistKeys={};for(var knownRow=1;knownRow<artistRows.length;knownRow+=1)knownArtistKeys[String(artistRows[knownRow][0])]=true;
  posts.forEach(function(post){var analysis=eeFastArticleIdentity_(post,registry);eePutArticleIdentity_(analysis,registry,knownArtistKeys);});
  if(posts.length)properties.setProperty("EE_APPLE_IDENTITY_INDEX",String(cursor+posts.length));else properties.setProperty("EE_APPLE_IDENTITY_COMPLETE","true");
  var result={status:posts.length?"OK":"COMPLETE",startIndex:cursor,analyzed:posts.length,nextIndex:cursor+posts.length};console.log(JSON.stringify(result));return result;}finally{eeReleaseWorkerLease_("IDENTITY");}
}

function eeDiscoverArtistsWorker() {
  if(!eeAcquireWorkerLease_("DISCOVERY",240000))return {status:"BUSY"};
  try{
    var sheet=eeArtistCatalogueSheet_(),values=sheet.getDataRange().getValues(),properties=PropertiesService.getScriptProperties(),cursor=Math.max(1,Number(properties.getProperty("EE_APPLE_ARTIST_DISCOVERY_INDEX")||1));
    eeSetExecutionDeadline_(Date.now()+180000);
    for(var row=cursor;row<values.length&&Date.now()<EE_APPLE_EXECUTION_DEADLINE;row+=1){
      if(String(values[row][7])!=="UNRESOLVED"){
        properties.setProperty("EE_APPLE_ARTIST_DISCOVERY_INDEX",String(row+1));
        continue;
      }
      var artistKey=String(values[row][0]),canonicalName=String(values[row][1]),representativePostId=String(values[row][11]||"");
      properties.setProperty("EE_APPLE_ARTIST_DISCOVERY_INDEX",String(row));
      try{
        var post=eeFetchPostById_(representativePostId),registry=eeArtistRegistry_(),artist=registry.artists.filter(function(value){return value.slug===artistKey;})[0]||{slug:artistKey,canonicalName:canonicalName,aliases:[],ambiguityClass:"provisional"};
        var catalogue=eeDiscoverArtistCatalogue_(artist,post);
        if(!catalogue||["RESOLVED","AMBIGUOUS","ERROR"].indexOf(String(catalogue.status))===-1)throw new Error("ARTIST_DISCOVERY_NO_TERMINAL_STATUS");
        properties.setProperty("EE_APPLE_ARTIST_DISCOVERY_INDEX",String(row+1));
        if(catalogue.status==="ERROR")console.log(JSON.stringify({artistKey:artistKey,canonicalName:canonicalName,terminalStatus:"ERROR",errorReason:catalogue.error||"APPLE_ARTIST_DISCOVERY_EXHAUSTED",nextCursor:row+1}));
      }catch(error){
        if(error&&error.retryable){
          properties.setProperty("EE_APPLE_ARTIST_DISCOVERY_INDEX",String(row));
          return {status:"RETRY_LATER",artistKey:artistKey,error:String(error.code||error.message)};
        }
        var errorReason=String(error.code||error.message||error);
        eePutArtistCatalogue_({artistKey:artistKey,canonicalName:canonicalName,identityConfidence:"ERROR",status:"ERROR",representativePostId:representativePostId,error:errorReason,categories:[]});
        properties.setProperty("EE_APPLE_ARTIST_DISCOVERY_INDEX",String(row+1));
        console.log(JSON.stringify({artistKey:artistKey,canonicalName:canonicalName,terminalStatus:"ERROR",errorReason:errorReason,nextCursor:row+1}));
      }
    }
    return {status:"OK",cursor:Number(properties.getProperty("EE_APPLE_ARTIST_DISCOVERY_INDEX")||1)};
  }finally{eeClearExecutionDeadline_();eeReleaseWorkerLease_("DISCOVERY");}
}

function eeRefreshStaleArtistsWorker() {
  if(!eeAcquireWorkerLease_("STALE_REFRESH",240000))return {status:"BUSY"};
  try{var sheet=eeArtistCatalogueSheet_(),values=sheet.getDataRange().getValues(),properties=PropertiesService.getScriptProperties(),cursor=Math.max(1,Number(properties.getProperty("EE_APPLE_STALE_REFRESH_INDEX")||1));eeSetExecutionDeadline_(Date.now()+180000);
  for(var row=cursor;row<values.length;row+=1){properties.setProperty("EE_APPLE_STALE_REFRESH_INDEX",String(row+1));if(String(values[row][7])!=="RESOLVED"||!values[row][10]||Date.parse(String(values[row][10]))>Date.now())continue;var registry=eeArtistRegistry_(),artist=registry.artists.filter(function(value){return value.slug===String(values[row][0]);})[0]||{slug:String(values[row][0]),canonicalName:String(values[row][1]),aliases:[],ambiguityClass:"provisional"},post=eeFetchPostById_(String(values[row][11]||""));try{eeDiscoverArtistCatalogue_(artist,post,true);return {status:"REFRESHED",artistKey:artist.slug,cursor:row+1};}catch(error){if(error&&error.retryable){properties.setProperty("EE_APPLE_STALE_REFRESH_INDEX",String(row));return {status:"RETRY_LATER",artistKey:artist.slug,error:String(error.code||error.message)};}return {status:"ERROR",artistKey:artist.slug,error:String(error.message||error)};}}
  properties.setProperty("EE_APPLE_STALE_REFRESH_INDEX","1");return {status:"COMPLETE",cursor:1};}finally{eeClearExecutionDeadline_();eeReleaseWorkerLease_("STALE_REFRESH");}
}

function eeAssembleArticlePayloadsWorker() {
  if(!eeAcquireWorkerLease_("ASSEMBLY",240000))return {status:"BUSY"};
  try{var properties=PropertiesService.getScriptProperties(),sheet=eeArticleIdentitySheet_(),values=sheet.getDataRange().getValues(),cursor=Math.max(1,Number(properties.getProperty("EE_APPLE_ASSEMBLY_INDEX")||1)),processed=0;
  for(var row=cursor;row<values.length&&processed<100;row+=1){properties.setProperty("EE_APPLE_ASSEMBLY_INDEX",String(row+1));var keys=JSON.parse(String(values[row][4]||"[]")),catalogues=keys.map(eeGetArtistCatalogue_).filter(function(record){return record&&record.status==="RESOLVED";});if(keys.length&&catalogues.length!==keys.length)continue;var post=eeFetchPostById_(String(values[row][0])),analysis={primaryArtistKeys:keys,primaryArtists:JSON.parse(String(values[row][5]||"[]")),people:[],identityConfidence:String(values[row][6]),articleType:String(values[row][9])},payload=eeAssemblePayloadFromCatalogues_(post,analysis,catalogues);eePutPayload_(post,payload,eePayloadHasRecommendations_(payload)?"READY":"EMPTY",String((payload.diagnostics||{}).emptyClassification||""),0);processed+=1;}
  return {status:"OK",processed:processed,cursor:Number(properties.getProperty("EE_APPLE_ASSEMBLY_INDEX")||1)};}finally{eeReleaseWorkerLease_("ASSEMBLY");}
}

function eeSeedArtistCataloguesFromGeneration2() {
  var values=eePayloadSheet_().getDataRange().getValues(),registry=eeArtistRegistry_(),seeded=0;
  for(var row=1;row<values.length;row+=1){if(String(values[row][5])!=="READY")continue;var payload=eeDecodePayloadCell_(values[row][4]);if(!eePayloadHasRecommendations_(payload)||Number(payload.generationVersion)!==2)continue;var names=((payload.subject||{}).primaryArtists||[]);if(names.length!==1)continue;var artist=registry.artists.filter(function(value){return eeNorm_(value.canonicalName)===eeNorm_(names[0]);})[0];if(!artist||eeGetArtistCatalogue_(artist.slug))continue;var identity=payload.identity||{};if(identity.level!=="HIGH")continue;eePutArtistCatalogue_({artistKey:artist.slug,canonicalName:artist.canonicalName,appleArtistId:identity.artistId||"",identityConfidence:"HIGH",status:"RESOLVED",categories:payload.categories,representativePostId:String(payload.postId)});seeded+=1;}
  return {status:"OK",seeded:seeded};
}

function eeArchitectureStatus() {
  var properties=PropertiesService.getScriptProperties(),identity=eeArticleIdentitySheet_().getDataRange().getValues(),artists=eeArtistCatalogueSheet_().getDataRange().getValues(),payloads=eePayloadSheet_().getDataRange().getValues(),result={postsAnalyzed:Math.max(0,identity.length-1),canonicalArtists:Math.max(0,artists.length-1),verifiedAppleIds:0,unresolvedArtists:0,ambiguousArtists:0,staleArtists:0,payloadStatus:{READY:0,EMPTY:{},ERROR:{}},appleCalls:Number(properties.getProperty("EE_APPLE_CALL_COUNT")||0),appleCacheHits:Number(properties.getProperty("EE_APPLE_CACHE_HIT_COUNT")||0),catalogueGenerations:Number(properties.getProperty("EE_APPLE_CATALOGUE_GENERATION_COUNT")||0),identityCursor:Number(properties.getProperty("EE_APPLE_IDENTITY_INDEX")||1),artistDiscoveryCursor:Number(properties.getProperty("EE_APPLE_ARTIST_DISCOVERY_INDEX")||1),assemblyCursor:Number(properties.getProperty("EE_APPLE_ASSEMBLY_INDEX")||1),staleRefreshCursor:Number(properties.getProperty("EE_APPLE_STALE_REFRESH_INDEX")||1),cooldownUntil:properties.getProperty("EE_APPLE_COOLDOWN_UNTIL")||null,mostRecentTransientFailure:properties.getProperty("EE_APPLE_LAST_TRANSIENT_FAILURE")||null};
  for(var row=1;row<artists.length;row+=1){if(artists[row][4])result.verifiedAppleIds+=1;if(artists[row][7]==="UNRESOLVED")result.unresolvedArtists+=1;if(artists[row][7]==="AMBIGUOUS")result.ambiguousArtists+=1;if(artists[row][10]&&Date.parse(String(artists[row][10]))<=Date.now())result.staleArtists+=1;}
  for(var index=1;index<payloads.length;index+=1){var status=String(payloads[index][5]||""),error=String(payloads[index][6]||"")||"UNCLASSIFIED";if(status==="READY")result.payloadStatus.READY+=1;else if(status==="EMPTY")result.payloadStatus.EMPTY[error]=(result.payloadStatus.EMPTY[error]||0)+1;else if(status==="ERROR")result.payloadStatus.ERROR[error]=(result.payloadStatus.ERROR[error]||0)+1;}
  console.log(JSON.stringify(result));return result;
}
'''


def build_code() -> str:
    code = CODE_SOURCE.read_text(encoding="utf-8")
    code = replace_function(code, "eeAppleSearch_", "eeAppleTvHtmlDecode_", APPLE_REQUESTS)
    code = replace_function(code, "eeAppleTvPush_", "eeAppleTvItemsFromHtml_", APPLE_TV_PUSH)
    code = replace_once(
        code,
        "  categoryLimit: 24,",
        '  generationVersion: 3,\n  artistIndexUrl: "https://archive.electriceyerock.com/proof/artist-index.json",',
        "generation version",
    )
    code = replace_once(
        code,
        "  minimumRequestIntervalMs: 3100,",
        "  minimumRequestIntervalMs: 10000,",
        "production Apple throttle",
    )
    code = replace_once(
        code,
        '    var artworkMatch=block.match(/"artwork":\\{"template":"((?:\\\\.|[^"\\\\])*)"/);',
        '    var artworkMatch=block.match(/"artwork":\\{"template":"((?:\\\\.|[^"\\\\])*)"/);\n'
        '    var descriptionMatch=block.match(/"description":"((?:\\\\.|[^"\\\\])*)"/);\n'
        '    var castMatches=block.match(/"name":"((?:\\\\.|[^"\\\\])*)"/g)||[];',
        "Apple TV metadata extraction",
    )
    code = replace_once(
        code,
        '          mediaType:/série|series|show/i.test(mediaType)?"TV Show":"Film"\n        },storefront,subject);',
        '          mediaType:/série|series|show/i.test(mediaType)?"TV Show":"Film",\n'
        '          description:descriptionMatch?eeAppleTvJsonDecode_(descriptionMatch[1]):"",\n'
        '          cast:castMatches.map(function(value){var match=value.match(/"name":"((?:\\\\.|[^"\\\\])*)"/);return match?eeAppleTvJsonDecode_(match[1]):"";}).filter(Boolean)\n'
        '        },storefront,subject);',
        "Apple TV metadata handoff",
    )
    code = replace_once(
        code,
        '  var response=UrlFetchApp.fetch(url,{\n    muteHttpExceptions:true,\n    headers:{"User-Agent":"Mozilla/5.0"}\n  });\n\n  if(response.getResponseCode()!==200){\n    throw new Error("Apple TV public search returned "+response.getResponseCode());\n  }',
        '  var response=eeAppleFetch_(url,{muteHttpExceptions:true,headers:{"User-Agent":"Mozilla/5.0"}},"APPLE_TV_SEARCH");',
        "Apple TV shared throttle",
    )
    code = replace_once(
        code,
        "function eeBackfillBatch() {",
        "function eeBackfillBatch(silent) {",
        "backfill batch signature",
    )
    code = replace_once(
        code,
        "    console.log(JSON.stringify(completeResult, null, 2));\n    return completeResult;",
        "    if (!silent) console.log(JSON.stringify(completeResult, null, 2));\n    return completeResult;",
        "quiet completion log",
    )
    code = replace_once(
        code,
        "  console.log(JSON.stringify(result, null, 2));\n\n  return result;",
        "  if (!silent) console.log(JSON.stringify(result, null, 2));\n\n  return result;",
        "quiet batch log",
    )
    target = "  var results = [];\n\n  posts.forEach(function(post) {"
    if target not in code:
        raise RuntimeError("Missing primary-walk result loop")
    code = code.replace(
        target,
        '  properties.setProperty("EE_APPLE_BACKFILL_COMPLETE", "false");\n'
        + "  var retryLater=null;\n"
        + target,
        1,
    )
    code = replace_once(
        code,
        '    } catch(error) {\n      results.push({\n        postId:String(post.id),\n        title:post.title,\n        status:"ERROR",\n        error:String(error && error.message || error)\n      });\n    }\n  });\n\n  var next = start + posts.length;',
        '    } catch(error) {\n      if(error&&error.retryable)retryLater={postId:String(post.id),status:"RETRY_LATER",error:String(error.code||error.message||error)};\n      else results.push({postId:String(post.id),title:post.title,status:"ERROR",error:String(error&&error.message||error)});\n    }\n  });\n\n  if(retryLater)return {status:"RETRY_LATER",startIndex:start,fetched:posts.length,nextIndex:start,results:results.concat([retryLater])};\n  var next = start + posts.length;',
        "transient cursor pinning",
    )
    code = replace_once(
        code,
        '    var hasRecommendations =\n      Array.isArray(payload.categories) &&\n      payload.categories.some(function(group) {\n        return Array.isArray(group.items) && group.items.length;\n      });',
        '    var hasRecommendations=eePayloadHasRecommendations_(payload);',
        "shared recommendation validity",
    )
    code = replace_once(
        code,
        'eePutPayload_(post, payload, "EMPTY", "No qualifying recommendations generated");',
        'eePutPayload_(post, payload, "EMPTY", String((payload.diagnostics||{}).emptyClassification||"EMPTY_OTHER"), retryCount);',
        "classified empty storage",
    )
    code = replace_once(
        code,
        "function eeProcessPost_(post) {",
        QUALITY_HELPERS + "\n\nfunction eeProcessPost_(post, retryCount) {",
        "process-post signature",
    )
    code = code.replace(
        'eePutPayload_(post, payload, "READY", "");',
        'eePutPayload_(post, payload, "READY", "", retryCount);',
        1,
    ).replace(
        'eePutPayload_(post, payload, "EMPTY", "No qualifying recommendations generated");',
        'eePutPayload_(post, payload, "EMPTY", "No qualifying recommendations generated", retryCount);',
        1,
    )
    code = replace_once(
        code,
        '        String(error && error.message || error)\n      );',
        '        String(error && error.message || error),\n        retryCount\n      );',
        "error retry persistence",
    )
    code = replace_once(
        code,
        '  if (sheet.getLastRow() === 0) sheet.appendRow(["postId", "canonicalUrl", "generatedAt", "storefront", "payloadJson", "status", "error"]);',
        '  if (sheet.getLastRow() === 0) sheet.appendRow(["postId", "canonicalUrl", "generatedAt", "storefront", "payloadJson", "status", "error", "retryCount"]);\n'
        '  else if (sheet.getLastColumn() < 8) sheet.getRange(1, 8).setValue("retryCount");',
        "backward-compatible retry column",
    )
    code = replace_once(
        code,
        "function eePutPayload_(post, payload, status, error) {",
        "function eePutPayload_(post, payload, status, error, retryCount) {",
        "put-payload signature",
    )
    code = replace_once(
        code,
        '  sheet.getRange(target, 1, 1, 7).setValues([[\n'
        '    String(post.id),\n'
        '    post.url || "",\n'
        '    new Date().toISOString(),\n'
        '    payload.storefront || EE_APPLE_CONFIG.storefront,\n'
        '    storedPayload,\n'
        '    status,\n'
        '    error || ""\n'
        '  ]]);',
        '  sheet.getRange(target, 1, 1, 8).setValues([[\n'
        '    String(post.id),\n'
        '    post.url || "",\n'
        '    new Date().toISOString(),\n'
        '    payload.storefront || EE_APPLE_CONFIG.storefront,\n'
        '    storedPayload,\n'
        '    status,\n'
        '    error || "",\n'
        '    Math.max(0, Number(retryCount || 0))\n'
        '  ]]);',
        "eight-column payload write",
    )
    code = replace_once(
        code,
        "function eeEntityHints_(post) {\n  var explicit = post.entityHints || post.entities || null;",
        'function eeEntityHints_(post) {\n  var reviewed=eeReviewedPostSubjects_(post.id);\n  if(reviewed.length)return {primaryArtists:reviewed,people:[],associatedPeople:[],collaborators:[],producers:[],sideProjects:[],relatedArtists:[],articleArtists:reviewed,existingAppleArtistIds:[]};\n  var explicit = post.entityHints || post.entities || null;',
        "reviewed subject overrides",
    )
    code = replace_once(
        code,
        '  ).map(eeNorm_);',
        '  );',
        "primary artist display spelling",
    )
    code = replace_once(
        code,
        '    people: eeUnique_(hints.people || []).map(eeNorm_),',
        '    people: eeUnique_(hints.people || []),',
        "people display spelling",
    )
    code = replace_once(
        code,
        '    associatedPeople: eeUnique_(hints.associatedPeople || hints.members || []).map(eeNorm_),',
        '    associatedPeople: eeUnique_(hints.associatedPeople || hints.members || []),',
        "associated people display spelling",
    )
    code = code.replace(
        'var subject=analysis.primaryArtists[0]||""',
        'var subject=eeNorm_(analysis.primaryArtists[0]||"")',
    ).replace(
        'var primary=analysis.primaryArtists[0]||""',
        'var primary=eeNorm_(analysis.primaryArtists[0]||"")',
    ).replace(
        '(analysis.primaryArtists[0]||"")',
        'eeNorm_(analysis.primaryArtists[0]||"")',
    )
    code = code.replace("eeNorm_eeNorm_", "eeNorm_")
    code = code.replace(
        "festival|tour|video|playlist|friday'?s playlist",
        "festival|tour|video|new|dates?|releases?|announces?|paris|album|single|song|track|show|tickets?|playlist|friday'?s playlist",
    ).replace(
        "festival|tour|video|photos?|playlist|friday'?s playlist",
        "festival|tour|video|new|dates?|releases?|announces?|paris|album|single|song|track|show|tickets?|photos?|playlist|friday'?s playlist",
    )
    code = code.replace(
        'existing && Array.isArray(existing.categories) && existing.categories.length',
        'eePayloadHasRecommendations_(existing)',
    ).replace(
        'existingNewest && Array.isArray(existingNewest.categories) && existingNewest.categories.length',
        'eePayloadHasRecommendations_(existingNewest)',
    )
    code = replace_once(
        code,
        '  if (cached) return eeDecodePayloadCell_(cached);',
        '  if(cached){var cachedPayload=eeDecodePayloadCell_(cached);return eePayloadHasRecommendations_(cachedPayload)?cachedPayload:null;}',
        "cached stale-ready rejection",
    )
    code = replace_once(
        code,
        '      var payload = eeDecodePayloadCell_(stored);\n      CacheService.getScriptCache().put(\n        key,\n        stored,\n        EE_APPLE_CONFIG.payloadCacheSeconds\n      );\n      return payload;',
        '      var payload=eeDecodePayloadCell_(stored);\n      if(!eePayloadHasRecommendations_(payload))return null;\n      CacheService.getScriptCache().put(key,stored,EE_APPLE_CONFIG.payloadCacheSeconds);\n      return payload;',
        "stale ready rejection",
    )
    code = replace_once(
        code,
        '    output=eeGetPayload_(params.postId)||output;',
        '    output=eePublicPayload_(eeGetPayload_(params.postId))||output;',
        "public payload stripping",
    )
    code = replace_once(
        code,
        'function eeAddCandidateToMap_(map,raw,query,analysis){\n  var item=eeCandidate_(raw,query,analysis);\n  if(!item)return;',
        'function eeAddCandidateToMap_(map,raw,query,analysis){\n  var item=eeCandidate_(raw,query,analysis);\n  if(!item)return false;',
        "candidate rejection accounting",
    )
    code = replace_once(
        code,
        '  if(!map[key]||item.relevanceScore>map[key].relevanceScore){\n    map[key]=item;\n  }\n}',
        '  if(!map[key]||item.relevanceScore>map[key].relevanceScore){map[key]=item;}\n  return true;\n}',
        "candidate acceptance accounting",
    )
    code = replace_once(
        code,
        '  var map={};\n  var musicResults=[];',
        '  var map={},musicResults=[];\n  var diagnostics={primaryArtists:analysis.primaryArtists.slice(),identity:null,searchIntents:plan.map(function(query){return query.category+":"+query.entity+":"+query.term;}),rawResultCount:0,acceptedCount:0,rejectedCount:0,relationshipRejectedCount:0,rejectionReasons:{}};',
        "generation diagnostics",
    )
    code = replace_once(
        code,
        '    (response.results||[]).forEach(function(raw){\n      eeAddCandidateToMap_(map,raw,query,analysis);\n    });',
        '    diagnostics.rawResultCount+=(response.results||[]).length;\n    (response.results||[]).forEach(function(raw){\n      if(eeAddCandidateToMap_(map,raw,query,analysis))diagnostics.acceptedCount+=1;\n      else{diagnostics.rejectedCount+=1;diagnostics.relationshipRejectedCount+=1;diagnostics.rejectionReasons.NO_QUALIFYING_RELATIONSHIP=(diagnostics.rejectionReasons.NO_QUALIFYING_RELATIONSHIP||0)+1;}\n    });',
        "raw and rejected result accounting",
    )
    code = replace_once(
        code,
        '  var identity=eeResolveIdentity_(analysis,musicResults);',
        '  var identity=eeResolveIdentity_(analysis,musicResults);\n  diagnostics.identity=identity;',
        "identity diagnostics",
    )
    code = replace_once(
        code,
        '      }catch(error){}\n    }\n  }else{',
        '      }catch(error){}\n    }\n    try{\n      eeAppleTvSearch_(analysis.primaryArtists[0]||"",settings.storefront).forEach(function(item){\n        var key="WATCH:tv:"+String(item.stableId);\n        if(!map[key]||item.relevanceScore>map[key].relevanceScore)map[key]=item;\n      });\n    }catch(error){if(error&&error.retryable)throw error;}\n  }else{',
        "Apple TV long-form enrichment",
    )
    code = replace_once(
        code,
        '    groups[category]=groups[category].slice(\n      0,\n      Math.min(EE_APPLE_CONFIG.categoryLimit,24)\n    );\n\n',
        '',
        "backend item cap",
    )
    code = replace_once(
        code,
        '  return {\n    schemaVersion:1,\n    generatedAt:new Date().toISOString(),',
        '  diagnostics.finalCategoryCounts={};\n  categories.forEach(function(group){diagnostics.finalCategoryCounts[group.category]=group.items.length;});\n  diagnostics.emptyClassification=categories.length?null:eeEmptyClassification_(diagnostics);\n  return {\n    schemaVersion:1,\n    generationVersion:EE_APPLE_CONFIG.generationVersion,\n    generatedAt:new Date().toISOString(),',
        "payload generation version and diagnostics",
    )
    code = replace_once(
        code,
        '    identity:identity,\n    categories:categories\n  };',
        '    identity:identity,\n    categories:categories,\n    diagnostics:diagnostics\n  };',
        "payload diagnostics",
    )
    code = replace_once(
        code,
        '    score=96;\n    tier="DIRECT";\n    reason="Official Apple Music video by the primary artist in the configured storefront.";',
        '    score=88;\n    tier="CLOSELY_RELATED";\n    reason="Official Apple Music video by the primary artist in the configured storefront.";',
        "music video ranking",
    )
    code = replace_once(
        code,
        '          : (eeContains_(creator,query.term)||eeContains_(title,query.term))',
        '          : ([].concat(raw.cast||[]).concat(raw.performers||[]).concat(raw.director||[]).some(function(name){return eeNorm_(name)===eeNorm_(query.term);})||(/documentary|documentaire|concert film|live concert|portrait|biograph/.test(eeNorm_(fullDescription))&&eeContains_(fullDescription,query.term)))',
        "WATCH metadata relationship",
    )
    code = replace_once(
        code,
        '      if(eeContains_(title,analysis.people[subjectIndex])){\n        score=92;tier="DIRECT";reason="Apple title directly names the article subject.";\n      }',
        '      var person=analysis.people[subjectIndex],credited=[].concat(raw.cast||[]).concat(raw.performers||[]).concat(raw.director||[]).some(function(name){return eeNorm_(name)===eeNorm_(person);});\n      if((query.category!=="WATCH"&&eeContains_(title,person))||(query.category==="WATCH"&&credited)){\n        score=92;tier="DIRECT";reason=query.category==="WATCH"?"Apple cast or credits identify the article subject.":"Apple title directly names the article subject.";\n      }',
        "title-only person rejection",
    )
    code = replace_once(
        code,
        '  } else if(!score&&query.category==="WATCH"&&primary&&eeContains_(combined,primary)){\n    var watchSpecific=eeContains_(title,primary)||eeNorm_(fullDescription).split(primary).length>2;\n    if(!watchSpecific)return null;\n    score=94;\n    tier="DIRECT";\n    reason="Title or Apple description is specifically about the primary artist.";\n  }',
        '  } else if(!score&&query.category==="WATCH"&&primary&&eeContains_(combined,primary)){\n    var watchCredits=[].concat(raw.cast||[]).concat(raw.performers||[]).concat(raw.director||[]);\n    var credited=watchCredits.some(function(name){return eeNorm_(name)===primary;});\n    var described=eeNorm_(fullDescription).split(primary).length>2&&/documentary|documentaire|concert film|live concert|portrait|biograph/.test(eeNorm_(fullDescription));\n    if(!credited&&!described)return null;\n    score=credited?97:96;tier="DIRECT";reason=credited?"Apple cast or credits identify the primary artist.":"Apple metadata describes substantial long-form content about the primary artist.";\n  }',
        "WATCH relationship requirement",
    )
    code = code.replace(
        '    }catch(error){\n      expandedAlbums=[];\n    }',
        '    }catch(error){if(error&&error.retryable)throw error;expandedAlbums=[];}',
    ).replace(
        '      }catch(error){\n        directAlbumRows=[];\n      }',
        '      }catch(error){if(error&&error.retryable)throw error;directAlbumRows=[];}',
    ).replace(
        '      }catch(error){}\n    }\n    try{',
        '      }catch(error){if(error&&error.retryable)throw error;}\n    }\n    try{',
        1,
    )
    code = replace_once(
        code,
        '      var payload = eeProcessPost_(post);\n      results.push({\n        postId:String(post.id),\n        status:"READY",\n        categories:(payload.categories || []).map(function(group){return [group.category,group.items.length];})\n      });',
        '      var payload=eeProcessPost_(post);\n      results.push({postId:String(post.id),status:eePayloadHasRecommendations_(payload)?"READY":"EMPTY",categories:(payload.categories||[]).map(function(group){return [group.category,group.items.length];})});',
        "newest post validity",
    )
    code = replace_once(
        code,
        "function eeGeneratePayload_(post) {",
        "function eeGeneratePayloadLegacy_(post) {",
        "legacy unique-artist discovery generator",
    )
    code = replace_once(
        code,
        "function doGet(event) {",
        ARTIST_REGISTRY + "\n\nfunction doGet(event) {",
        "artist registry architecture",
    )
    debug_start = code.index("function eeRetryBackfillFrom9()")
    code = code[:debug_start].rstrip() + WORKER + "\n"
    return code


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "Electric-Eye-Theme.xml").write_text(build_theme(), encoding="utf-8")
    (OUT / "Code.gs").write_text(build_code(), encoding="utf-8")


if __name__ == "__main__":
    main()
