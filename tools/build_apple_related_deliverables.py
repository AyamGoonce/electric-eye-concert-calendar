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
var EE_APPLE_DISCOVERY_DIAGNOSTIC=null;
function eeSetExecutionDeadline_(value){EE_APPLE_EXECUTION_DEADLINE=Number(value||0);}
function eeClearExecutionDeadline_(){EE_APPLE_EXECUTION_DEADLINE=0;}

function eeDiscoveryDiagnosticStart_(artist) {
  var diagnostic={artistKey:String((artist||{}).slug||""),canonicalName:String((artist||{}).canonicalName||""),startedAt:Date.now(),queries:[],appleCalls:0,cacheHits:0,finished:false};
  EE_APPLE_DISCOVERY_DIAGNOSTIC=diagnostic;
  return diagnostic;
}

function eeDiscoveryDiagnosticQuery_(query) {
  var diagnostic=EE_APPLE_DISCOVERY_DIAGNOSTIC;
  if(!diagnostic)return null;
  var entry={term:String((query||{}).term||""),entity:String((query||{}).entity||""),category:String((query||{}).category||""),candidateCount:0,accepted:0,rejected:0,reasons:{}};
  diagnostic.queries.push(entry);return entry;
}

function eeDiscoveryDiagnosticCandidates_(entry,response) {if(entry)entry.candidateCount=((response||{}).results||[]).length;}
function eeDiscoveryDiagnosticDecision_(entry,accepted,reason) {if(!entry)return;var key=String(reason||"UNSPECIFIED");if(accepted)entry.accepted+=1;else entry.rejected+=1;entry.reasons[key]=(entry.reasons[key]||0)+1;}
function eeDiscoveryDiagnosticAppleCall_(){if(EE_APPLE_DISCOVERY_DIAGNOSTIC)EE_APPLE_DISCOVERY_DIAGNOSTIC.appleCalls+=1;}
function eeDiscoveryDiagnosticCacheHit_(){if(EE_APPLE_DISCOVERY_DIAGNOSTIC)EE_APPLE_DISCOVERY_DIAGNOSTIC.cacheHits+=1;}
function eeDiscoveryDiagnosticEnrichment_(state){if(EE_APPLE_DISCOVERY_DIAGNOSTIC)EE_APPLE_DISCOVERY_DIAGNOSTIC.enrichment=state||null;}

function eeDiscoveryDiagnosticStopReason_(error) {
  var value=String((error&&error.code)||(error&&error.message)||"");
  if(/(?:^|_)HTTP_403(?:$|_)/.test(value))return "403";
  if(/(?:^|_)HTTP_429(?:$|_)/.test(value))return "429";
  if(value.indexOf("HEADROOM")!==-1)return "HEADROOM";
  if(value.indexOf("COOLDOWN")!==-1)return "COOLDOWN";
  return "";
}

function eeDiscoveryDiagnosticFinish_(diagnostic,status,reason,error) {
  if(!diagnostic||diagnostic.finished)return;
  diagnostic.finished=true;
  console.log(JSON.stringify({type:"APPLE_ARTIST_DISCOVERY",artistKey:diagnostic.artistKey,canonicalName:diagnostic.canonicalName,queries:diagnostic.queries,appleCalls:diagnostic.appleCalls,cacheHits:diagnostic.cacheHits,terminalStatus:String(status||""),terminalReason:String(reason||""),elapsedMs:Math.max(0,Date.now()-diagnostic.startedAt),stoppedBy:eeDiscoveryDiagnosticStopReason_(error),enrichment:diagnostic.enrichment||null}));
  if(EE_APPLE_DISCOVERY_DIAGNOSTIC===diagnostic)EE_APPLE_DISCOVERY_DIAGNOSTIC=null;
}

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
      eeDiscoveryDiagnosticAppleCall_();
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
  if(cached){eeDiscoveryDiagnosticCacheHit_();var properties=PropertiesService.getScriptProperties();properties.setProperty("EE_APPLE_CACHE_HIT_COUNT",String(Number(properties.getProperty("EE_APPLE_CACHE_HIT_COUNT")||0)+1));return JSON.parse(cached);}
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
  if(cached){eeDiscoveryDiagnosticCacheHit_();var properties=PropertiesService.getScriptProperties();properties.setProperty("EE_APPLE_CACHE_HIT_COUNT",String(Number(properties.getProperty("EE_APPLE_CACHE_HIT_COUNT")||0)+1));return JSON.parse(cached);}
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

function eePayloadCategoryCounts_(payload) {
  var counts={};
  ((payload||{}).categories||[]).forEach(function(group){
    var category=String((group||{}).category||"");
    if(category)counts[category]=(counts[category]||0)+((group&&group.items)||[]).length;
  });
  return counts;
}

function eePayloadAtLeastAsUseful_(candidate,existing) {
  if(!eePayloadHasRecommendations_(candidate))return false;
  if(!eePayloadHasRecommendations_(existing))return true;
  var next=eePayloadCategoryCounts_(candidate),prior=eePayloadCategoryCounts_(existing);
  var nextItems={};((candidate||{}).categories||[]).forEach(function(group){
    nextItems[group.category]=nextItems[group.category]||{};(group.items||[]).forEach(function(item){nextItems[group.category][String(item.stableId||item.url||item.title||"")]=true;});
  });
  return Object.keys(prior).every(function(category){
    if(Number(next[category]||0)<Number(prior[category]||0))return false;
    var available=nextItems[category]||{};
    var priorGroup=((existing||{}).categories||[]).filter(function(group){return group.category===category;})[0]||{};
    return (priorGroup.items||[]).every(function(item){return !!available[String(item.stableId||item.url||item.title||"")];});
  });
}

function eePrimaryRecommendationRank_(item,primaryArtists,primaryArtistIds) {
  var itemId=String((item||{}).appleArtistId||""),creator=eeNorm_((item||{}).creator||"");
  if(itemId&&(primaryArtistIds||[]).map(String).indexOf(itemId)!==-1)return 0;
  if((primaryArtists||[]).some(function(name){return creator===eeNorm_(name);}))return 0;
  return 1;
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


PRODUCTION_ORCHESTRATOR = r'''
var EE_APPLE_PRODUCTION_MAX_ATTEMPTS_PER_RUN=1;
var EE_APPLE_PRODUCTION_TIME_LIMIT_MS=150000;
var EE_APPLE_PRODUCTION_NEWEST_SCAN=12;

function eeStoredPayloadGeneration_(stored) {try{return Number((eeDecodePayloadCell_(stored)||{}).generationVersion||0);}catch(error){return 0;}}

function eeProductionPayloadState_() {
  var values=eePayloadSheet_().getDataRange().getValues(),map={};
  for(var row=1;row<values.length;row+=1)map[String(values[row][0])]={status:String(values[row][5]||""),generationVersion:eeStoredPayloadGeneration_(values[row][4]),hasRecommendations:String(values[row][5]||"")==="READY"&&eeStoredPayloadHasRecommendations_(values[row][4]),error:String(values[row][6]||""),retryCount:Math.max(0,Number(values[row][7]||0))};
  return map;
}

function eeProductionNeedsPost_(state) {
  if(!state)return true;if(state.status==="READY"&&state.hasRecommendations)return false;if(state.status==="EMPTY"&&state.generationVersion>=EE_APPLE_CONFIG.generationVersion)return false;
  if(state.status==="ERROR"&&eeEnrichmentTransient_(state.error||""))return true;
  if(state.status==="ERROR"&&state.generationVersion>=EE_APPLE_CONFIG.generationVersion&&state.retryCount>=2)return false;
  return true;
}

function eeProductionMaintenanceStep_(properties,deadline) {
  var phases=["DISCOVERY","ENRICHMENT","ASSEMBLY"],index=Math.max(0,Number(properties.getProperty("EE_APPLE_PRODUCTION_MAINTENANCE_PHASE")||0))%phases.length,phase=phases[index],result;
  if(Date.now()>=deadline-15000)return {phase:phase,status:"HEADROOM"};
  eeSetExecutionDeadline_(deadline);
  if(phase==="DISCOVERY")result=eeDiscoverArtistsMaintenanceWorker_();
  else if(phase==="ENRICHMENT")result=eeRefreshStaleArtistsMaintenanceWorker_();
  else result=eeAssembleArticlePayloadsMaintenanceWorker_();
  properties.setProperty("EE_APPLE_PRODUCTION_MAINTENANCE_PHASE",String((index+1)%phases.length));
  return {phase:phase,status:String((result||{}).status||""),result:result||null};
}

function eeAppleRecommendationsProductionWorker() {
  if(!eeAppleSettings_().enabled)return {status:"DISABLED"};
  var properties=PropertiesService.getScriptProperties(),cooldownUntil=Number(properties.getProperty("EE_APPLE_COOLDOWN_UNTIL")||0);
  if(cooldownUntil>Date.now()){var cooling={status:"COOLDOWN",generationVersion:EE_APPLE_CONFIG.generationVersion,attempted:0,ready:0,empty:0,error:0,retryLater:0,retryAfter:new Date(cooldownUntil).toISOString(),elapsedMs:0};console.log(JSON.stringify(cooling));return cooling;}
  if(!eeAcquireWorkerLease_("PRODUCTION",240000))return {status:"BUSY"};
  var started=Date.now(),deadline=started+EE_APPLE_PRODUCTION_TIME_LIMIT_MS,generation=String(EE_APPLE_CONFIG.generationVersion),state=eeProductionPayloadState_(),attemptedThisRun={},stopRequested=false;
  var totals={status:"OK",generationVersion:EE_APPLE_CONFIG.generationVersion,attempted:0,ready:0,empty:0,error:0,retryLater:0,skippedReady:0,newestAttempted:0,archiveAttempted:0,nextCursor:1,maintenance:null,elapsedMs:0};
  if(properties.getProperty("EE_APPLE_PRODUCTION_GENERATION")!==generation){properties.setProperty("EE_APPLE_PRODUCTION_GENERATION",generation);properties.setProperty("EE_APPLE_PRODUCTION_INDEX","1");}
  eeSetExecutionDeadline_(deadline);
  try{
    function processPost(post,source){
      if(!post||totals.attempted>=EE_APPLE_PRODUCTION_MAX_ATTEMPTS_PER_RUN||Date.now()>=deadline)return false;var postId=String(post.id),prior=state[postId]||null;if(attemptedThisRun[postId])return false;
      if(!eeProductionNeedsPost_(prior)){if(prior&&prior.status==="READY")totals.skippedReady+=1;return false;}
      attemptedThisRun[postId]=true;totals.attempted+=1;if(source==="NEWEST")totals.newestAttempted+=1;else totals.archiveAttempted+=1;
      try{var payload=eeProcessPost_(post,prior?prior.retryCount+1:0),ready=eePayloadHasRecommendations_(payload);if(ready)totals.ready+=1;else totals.empty+=1;state[postId]={status:ready?"READY":"EMPTY",generationVersion:EE_APPLE_CONFIG.generationVersion,hasRecommendations:ready,retryCount:prior?prior.retryCount+1:0};}
      catch(error){if(error&&(error.retryable||eeEnrichmentTransient_(error))){totals.retryLater+=1;totals.status="RETRY_LATER";stopRequested=true;return false;}totals.error+=1;state[postId]={status:"ERROR",generationVersion:EE_APPLE_CONFIG.generationVersion,hasRecommendations:false,error:String(error&&error.message||error),retryCount:prior?prior.retryCount+1:1};}
      return true;
    }
    var newest=eeFetchPosts_(1,EE_APPLE_PRODUCTION_NEWEST_SCAN);
    for(var index=0;index<newest.length&&!stopRequested&&totals.attempted<EE_APPLE_PRODUCTION_MAX_ATTEMPTS_PER_RUN&&Date.now()<deadline;index+=1)if(!attemptedThisRun[String(newest[index].id)]&&eeProductionNeedsPost_(state[String(newest[index].id)]||null)){processPost(newest[index],"NEWEST");break;}
    var cursor=Math.max(1,Number(properties.getProperty("EE_APPLE_PRODUCTION_INDEX")||1));
    while(!stopRequested&&totals.attempted<EE_APPLE_PRODUCTION_MAX_ATTEMPTS_PER_RUN&&Date.now()<deadline){var posts=eeFetchPosts_(cursor,25);if(!posts.length){cursor=1;properties.setProperty("EE_APPLE_PRODUCTION_INDEX","1");break;}var found=false;for(var row=0;row<posts.length&&!stopRequested&&totals.attempted<EE_APPLE_PRODUCTION_MAX_ATTEMPTS_PER_RUN&&Date.now()<deadline;row+=1){var post=posts[row];cursor+=1;properties.setProperty("EE_APPLE_PRODUCTION_INDEX",String(cursor));if(attemptedThisRun[String(post.id)]||!eeProductionNeedsPost_(state[String(post.id)]||null)){if((state[String(post.id)]||{}).status==="READY")totals.skippedReady+=1;continue;}found=true;processPost(post,"ARCHIVE");break;}if(found)continue;if(posts.length<25){cursor=1;properties.setProperty("EE_APPLE_PRODUCTION_INDEX","1");break;}}
    if(!stopRequested)totals.maintenance=eeProductionMaintenanceStep_(properties,deadline);
    totals.nextCursor=Math.max(1,Number(properties.getProperty("EE_APPLE_PRODUCTION_INDEX")||1));totals.elapsedMs=Date.now()-started;if(Date.now()>=deadline&&totals.status==="OK")totals.status="TIME_LIMIT";console.log(JSON.stringify(totals));return totals;
  }finally{eeClearExecutionDeadline_();eeReleaseWorkerLease_("PRODUCTION");}
}

/* Single installed production trigger. */
function eeDiscoverArtistsWorker() {return eeAppleRecommendationsProductionWorker();}
'''


LEGACY_MAINTENANCE_ENTRY_POINTS = r'''
/* Old scheduled entry points remain intentionally idle: the single production
   worker rotates through their internal maintenance implementations. */
function eeRefreshStaleArtistsWorker() {return {status:"LEGACY_TRIGGER_IDLE",productionTrigger:"eeDiscoverArtistsWorker"};}
function eeAssembleArticlePayloadsWorker() {return {status:"LEGACY_TRIGGER_IDLE",productionTrigger:"eeDiscoverArtistsWorker"};}
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

function eeTitleArtistCandidate_(title) {
  title=String(title||"");
  var concert=title.match(/^(.+?)\s+@\s+/);
  var action=title.match(/^(.+?)\s+(?:announce|announces|release|releases|share|shares|unveil|unveils|return|returns|perform|performs)\b/i);
  var album=title.match(/^album review\s*(?::|[–-])\s*(.+?)(?:\s+[–-]\s+|$)/i);
  return String((concert||action||album||[])[1]||"").trim();
}

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
    var structuralArtist=names.some(function(name){return !!structuralLabels[eeNorm_(name)];});
    var titleCandidate=eeNorm_(eeTitleArtistCandidate_(title));
    var independentStructuralTitle=structuralArtist&&names.some(function(name){return eeNorm_(name)===titleCandidate;});
    var exactLabel=names.some(function(name){var key=eeNorm_(name);return normalizedLabels[key]&&!structuralLabels[key];});
    var titleMatch=names.some(function(name){return eeExactEntityInText_(title,name);});
    var articleKnown=(artist.articleIds||[]).map(String).indexOf(postId)!==-1;
    var reviewedKnown=(artist.reviewedArticleIds||[]).map(String).indexOf(postId)!==-1;
    var relationshipTerms=[]
      .concat(artist.members||[],artist.formerMembers||[],artist.associatedActs||[],artist.sideProjects||[],artist.keywords||[]);
    var relationshipHits=relationshipTerms.filter(function(name){return eeExactEntityInText_(title+" "+body,name);});
    var mentions=names.reduce(function(total,name){var needle=eeNorm_(name),hay=eeNorm_(body);return total+(needle?hay.split(needle).length-1:0);},0);
    var ambiguous=artist.ambiguityClass&&artist.ambiguityClass!=="distinctive";
    var accepted=reviewedKnown||independentStructuralTitle||(!structuralArtist&&articleKnown)||(!structuralArtist&&!ambiguous&&(exactLabel||titleMatch))||(!structuralArtist&&ambiguous&&exactLabel&&(relationshipHits.length>0||mentions>=2));
    return {accepted:accepted,score:reviewedKnown?125:articleKnown?120:independentStructuralTitle?115:exactLabel&&relationshipHits.length?110:exactLabel&&mentions>=2?105:exactLabel?96:titleMatch?88:0,evidence:[reviewedKnown&&"reviewed article association",articleKnown&&!structuralArtist&&"existing artist-index article association",independentStructuralTitle&&"independent title-derived artist identity",exactLabel&&"exact Blogger artist label",titleMatch&&"bounded title identity",relationshipHits.length&&("relationship corroboration: "+relationshipHits.join(", ")),mentions>=2&&"repeated body mentions"].filter(Boolean),ambiguous:ambiguous};
  }
  if(override){
    (override.primaryArtists||[]).forEach(function(name){var artist=(registry.artists||[]).filter(function(value){return eeNorm_(value.canonicalName)===eeNorm_(name);})[0];if(artist)matches.push({artist:artist,score:130,evidence:override.identityEvidence||["reviewed article override"],ambiguous:false});});
  }else{
    (registry.artists||[]).forEach(function(artist){var result=evidenceFor(artist);if(result.accepted)matches.push({artist:artist,score:result.score,evidence:result.evidence,ambiguous:result.ambiguous});});
  }
  if(!matches.length&&!override){
    var candidate=eeTitleArtistCandidate_(title);
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
var EE_APPLE_ARTIST_TRANSIENT_RETRY_LIMIT=3;
var EE_APPLE_ARTIST_DEFERRED_RETRY_MS=6*60*60*1000;
var EE_APPLE_CLEAR_IDENTITY_RETRY_MS=15*60*1000;
function eeArtistClearCanonical_(artist){return String((artist||{}).ambiguityClass||"")==="distinctive";}

function eeArtistCatalogueSheet_() {
  var header=["artistKey","canonicalName","registrySchemaVersion","catalogueSchemaVersion","appleArtistId","musicBrainzId","identityConfidence","status","catalogueJson","generatedAt","staleAfter","representativePostId","error","transientRetryCount","lastTransientError","retryAfter"],sheet=eeNamedSheet_("Apple Artists",header);
  if(sheet.getLastColumn()<header.length)sheet.getRange(1,14,1,3).setValues([["transientRetryCount","lastTransientError","retryAfter"]]);
  return sheet;
}

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
  for(var row=1;row<values.length;row+=1)if(String(values[row][0])===String(artistKey)){var payload=String(values[row][8]||""),staleAfter=String(values[row][10]||"");return {artistKey:String(values[row][0]),canonicalName:String(values[row][1]),appleArtistId:String(values[row][4]||""),musicBrainzId:String(values[row][5]||""),identityConfidence:String(values[row][6]||""),status:String(values[row][7]||""),catalogue:payload?eeDecodePayloadCell_(payload):null,generatedAt:String(values[row][9]||""),staleAfter:staleAfter,isStale:!!staleAfter&&Date.parse(staleAfter)<=Date.now(),representativePostId:String(values[row][11]||""),error:String(values[row][12]||""),transientRetryCount:Math.max(0,Number(values[row][13]||0)),lastTransientError:String(values[row][14]||""),retryAfter:String(values[row][15]||"")};}
  return null;
}

function eePutArtistCatalogue_(record) {
  var sheet=eeArtistCatalogueSheet_(),now=new Date(),generated=record.generatedAt||now.toISOString(),stale=record.staleAfter||new Date(now.getTime()+30*86400000).toISOString();
  var catalogue={schemaVersion:1,generationVersion:EE_APPLE_CONFIG.generationVersion,artistKey:record.artistKey,canonicalName:record.canonicalName,categories:record.categories||[]};
  if(record.enrichment)catalogue.enrichment=record.enrichment;
  eeUpsertRow_(sheet,0,record.artistKey,[record.artistKey,record.canonicalName,1,1,record.appleArtistId||"",record.musicBrainzId||"",record.identityConfidence||"",record.status||"UNRESOLVED",eeEncodePayloadCell_(catalogue),generated,stale,record.representativePostId||"",record.error||"",Math.max(0,Number(record.transientRetryCount||0)),record.lastTransientError||"",record.retryAfter||""]);
}

function eeAssemblePayloadFromCatalogues_(post,analysis,catalogues) {
  var allowedCatalogues={};(analysis.primaryArtistKeys||[]).forEach(function(key,index){allowedCatalogues[String(key)]=eeNorm_((analysis.primaryArtists||[])[index]||"");});
  catalogues=(catalogues||[]).filter(function(record){var expected=allowedCatalogues[String(record.artistKey||"")];return !!expected&&expected===eeNorm_(record.canonicalName||"");});
  var groups={LISTEN:{},WATCH:{},READ:{}},articleText=String(post.title||"")+" "+String(post.content||"").replace(/<[^>]+>/g," ");
  catalogues.forEach(function(record){((record.catalogue||{}).categories||[]).forEach(function(group){(group.items||[]).forEach(function(item){var ranked=JSON.parse(JSON.stringify(item)),sourceUrl=ranked.url||ranked.canonicalAppleUrl||"",trackedUrl=sourceUrl?eeAffiliateUrl_(group.category,sourceUrl):"";if(sourceUrl&&!trackedUrl)return;if(trackedUrl)ranked.url=trackedUrl;var boost=0;if(ranked.title&&eeExactEntityInText_(articleText,ranked.title))boost+=6;if(analysis.articleType==="interview"&&ranked.creator&&eeExactEntityInText_(post.title||"",ranked.creator))boost+=3;ranked.relevanceScore=Number(ranked.relevanceScore||0)+boost;var key=String(ranked.stableId||ranked.url||ranked.title),existing=groups[group.category]&&groups[group.category][key];if(groups[group.category]&&(!existing||Number(ranked.relevanceScore||0)>Number(existing.relevanceScore||0)))groups[group.category][key]=ranked;});});});
  var primaryIds=catalogues.map(function(record){return record.appleArtistId;}).filter(Boolean),categories=[];["LISTEN","WATCH","READ"].forEach(function(category){var items=Object.keys(groups[category]).map(function(key){return groups[category][key];});items.sort(function(a,b){return eePrimaryRecommendationRank_(a,analysis.primaryArtists,primaryIds)-eePrimaryRecommendationRank_(b,analysis.primaryArtists,primaryIds)||Number(b.relevanceScore||0)-Number(a.relevanceScore||0)||String(a.title).localeCompare(String(b.title));});if(items.length)categories.push({category:category,items:items});});
  return {schemaVersion:1,generationVersion:EE_APPLE_CONFIG.generationVersion,generatedAt:new Date().toISOString(),postId:String(post.id),canonicalUrl:post.url||"",storefront:eeAppleSettings_().storefront,subject:{title:post.title||"",primaryArtists:analysis.primaryArtists,people:analysis.people||[]},identity:{level:analysis.identityConfidence,artistId:catalogues.length===1?catalogues[0].appleArtistId||null:null,confidenceScore:analysis.identityConfidence==="HIGH"?100:75},categories:categories,diagnostics:{architecture:"ARTIST_REGISTRY_V1",artistKeys:analysis.primaryArtistKeys,cacheHits:catalogues.length,emptyClassification:categories.length?null:(analysis.primaryArtistKeys.length?"EMPTY_NO_QUALIFYING_RELATIONSHIP":"EMPTY_NO_SUBJECT")}};
}

function eeReadOnlySheet_(name) {var settings=eeAppleSettings_();if(!settings.spreadsheetId)throw new Error("EE_APPLE_SPREADSHEET_ID is not configured");var sheet=SpreadsheetApp.openById(settings.spreadsheetId).getSheetByName(name);if(!sheet)throw new Error("Missing sheet: "+name);return sheet;}

function eeReadyAuditArtistByName_(name,registry) {var needle=eeNorm_(name),matches=((registry||{}).artists||[]).filter(function(artist){return [artist.canonicalName].concat(artist.aliases||[],artist.alternateSpellings||[]).some(function(value){return eeNorm_(value)===needle;});});return matches.length===1?matches[0]:null;}

function eeReadyAuditEquivalentNames_(name,registry) {
  var artist=eeReadyAuditArtistByName_(name,registry),names=[name];if(!artist)return eeUnique_(names.map(eeNorm_));names=names.concat([artist.canonicalName],artist.aliases||[],artist.alternateSpellings||[]);
  var base=eeNorm_(artist.canonicalName).replace(/^the /,""),articleIds=artist.articleIds||[];if(/^the /.test(eeNorm_(artist.canonicalName)))names.push(base);
  ((registry||{}).artists||[]).forEach(function(candidate){var candidateBase=eeNorm_(candidate.canonicalName).replace(/^the /,"");if(base!==candidateBase||eeNorm_(candidate.canonicalName)===eeNorm_(artist.canonicalName))return;var reviewed=(candidate.articleIds||[]).some(function(id){return articleIds.indexOf(id)!==-1;});if(reviewed)names=names.concat([candidate.canonicalName],candidate.aliases||[],candidate.alternateSpellings||[]);});
  return eeUnique_(names.map(eeNorm_));
}

function eeReadyAuditTitleSubjects_(payload,registry) {
  var title=String(((payload.subject||{}).title)||""),lead=title.split(/\s+@\s+|\s+[–—-]\s+|:\s+/)[0],explicit=/\b(?:co[- ]?headlin|joint tour|double bill)\b/i.test(title),parts=explicit?lead.split(/\s+(?:and|&)\s+/i):[lead],found=[];
  parts.forEach(function(part){((registry||{}).artists||[]).forEach(function(artist){var names=[artist.canonicalName].concat(artist.aliases||[],artist.alternateSpellings||[]);if(names.some(function(name){return eeExactEntityInText_(part,name);}))found.push(artist);});});
  return found.filter(function(artist){return !/^(?:fnac|fnac forum)$/i.test(String(artist.canonicalName||""));});
}

function eeReadyAuditExplicitPersonSubject_(title) {
  var text=String(title||""),interview=text.match(/(?:interview|conversation)\s+with\s+(.+?)(?:\s*-\s*video\s*interview|\s*\(video[^)]*\)|$)/i);if(interview)return String(interview[1]).trim();var match=text.match(/^\s*([A-ZÀ-ÖØ-Þ][A-Za-zÀ-ÖØ-öø-ÿ'’.-]+(?:\s+[A-ZÀ-ÖØ-Þ][A-Za-zÀ-ÖØ-öø-ÿ'’.-]+){1,2})\s+(?:at|with|is|was|drummer|guitarist|bassist|singer|of)\b/i);return match?String(match[1]).trim():"";
}

function eeCorrectedPayloadIdentity_(payload,registry) {var subject=(payload.subject||{}),post={id:String(payload.postId||""),url:String(payload.canonicalUrl||""),title:String(subject.title||""),labels:[],content:""},analysis=eeFastArticleIdentity_(post,registry),titleArtists=eeReadyAuditTitleSubjects_(payload,registry),person=eeReadyAuditExplicitPersonSubject_(post.title);if(person&&!/^\s*(a|the)\s+/i.test(person)){var personArtist=eeReadyAuditArtistByName_(person,registry);analysis.primaryArtists=[personArtist?personArtist.canonicalName:person];analysis.primaryArtistKeys=[personArtist?personArtist.slug:eeNorm_(person).replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"")];analysis.ambiguous=false;analysis.identityConfidence="HIGH";return analysis;}if(titleArtists.length){var venueTitle=/\s+@\s+/i.test(post.title),explicit=/\b(?:co[- ]?headlin|joint tour|double bill)\b/i.test(post.title);if(venueTitle||explicit){analysis.primaryArtists=eeUnique_(titleArtists.map(function(artist){return artist.canonicalName;}));analysis.primaryArtistKeys=eeUnique_(titleArtists.map(function(artist){return artist.slug;}));analysis.ambiguous=false;analysis.identityConfidence="HIGH";}}return analysis;}

function eeReadyAuditRelationshipNames_(artists,registry) {
  var names=[],primary=eeUnique_((artists||[]).map(function(artist){return eeNorm_(artist.canonicalName);}).filter(Boolean));
  (artists||[]).forEach(function(artist){names=names.concat([artist.canonicalName].concat(artist.aliases||[],artist.alternateSpellings||[],artist.members||[],artist.formerMembers||[],artist.sideProjects||[],artist.associatedActs||[]));});
  ((registry||{}).artists||[]).forEach(function(artist){var related=[].concat(artist.members||[],artist.formerMembers||[],artist.sideProjects||[]).map(eeNorm_);if(primary.some(function(name){return related.indexOf(name)!==-1;}))names=names.concat([artist.canonicalName].concat(artist.aliases||[],artist.alternateSpellings||[]));});
  var profiles=[];try{profiles=eeEntityProfiles_();}catch(error){}profiles.forEach(function(profile){var profileNames=[profile.name].concat(profile.aliases||[]).map(eeNorm_),relations=[].concat(profile.members||[],profile.collaborators||[],profile.producers||[],profile.sideProjects||[],profile.relatedArtists||[]);if(primary.some(function(name){return profileNames.indexOf(name)!==-1;}))names=names.concat(profileNames,relations);if(relations.map(eeNorm_).some(function(name){return primary.indexOf(name)!==-1;}))names=names.concat(profileNames);});
  primary.forEach(function(name){names=names.concat(eeReadyAuditEquivalentNames_(name,registry));});
  return eeUnique_(names.map(eeNorm_).filter(Boolean));
}

function eeReadyAuditItemCheck_(item,category,allowed,correctedNames) {
  item=item||{};category=String(category||item.category||"").toUpperCase();var creator=String(item.creator||"").trim(),creatorAllowed=!creator||allowed.indexOf(eeNorm_(creator))!==-1,text=[item.title,item.description,item.cast,item.director,item.relationshipContext,item.relevanceReason].join(" "),descriptionText=String(item.description||"")+" "+String(item.relationshipContext||"")+" "+String(item.relevanceReason||""),subjectMatch=correctedNames.some(function(name){var normalized=eeNorm_(name),title=eeNorm_(item.title||""),description=eeNorm_(descriptionText);return (title===normalized||title.indexOf(normalized+" ")===0||description.indexOf(" "+normalized+" ")!==-1||description.indexOf(normalized+" ")===0)&&!(normalized==="nails"&&/nine inch nails|nail biting|fingernail/i.test(eeNorm_(text)));});
  if(category==="READ"){var directCreator=correctedNames.some(function(name){return eeNorm_(creator)===eeNorm_(name);}),readValid=directCreator||subjectMatch||/primary artist|article subject|directly concern|substantially feature/i.test(String(item.relationshipContext||item.relevanceReason||""));return {valid:readValid,creatorConflict:false,reason:readValid?"READ_SUBJECT_EVIDENCE":"READ_RELEVANCE_UNVERIFIED"};}
  if(category==="WATCH"){var valid=creatorAllowed||subjectMatch||/primary artist|article subject|directly concern/i.test(String(item.relationshipContext||item.relevanceReason||""));return {valid:valid,creatorConflict:!valid&&!!creator,reason:valid?"WATCH_CREDIT_OR_SUBJECT_EVIDENCE":"WATCH_RELEVANCE_UNVERIFIED"};}
  return {valid:creatorAllowed,creatorConflict:!creatorAllowed&&!!creator,reason:creatorAllowed?"LISTEN_CREATOR_ALLOWED":"LISTEN_CREATOR_UNRELATED"};
}

function eeReadyAuditFinding_(payload,registry,sharedIds,artistStates,safetyContext) {
  payload=payload||{};safetyContext=safetyContext||{};var structural={},reasons=[],advisories=[],safetyBlocks=[],categoryReasons=[],subject=(payload.subject||{}),storedNames=subject.primaryArtists||[],keys=(payload.diagnostics||{}).artistKeys||[],storedId=String((payload.identity||{}).artistId||""),analysis=eeCorrectedPayloadIdentity_(payload,registry),correctedNames=analysis.primaryArtists||[],correctedKeys=analysis.primaryArtistKeys||[];
  (registry.structuralLabels||[]).forEach(function(value){structural[eeNorm_(value)]=true;});
  var correctedEquivalent=[];correctedNames.forEach(function(name){correctedEquivalent=correctedEquivalent.concat(eeReadyAuditEquivalentNames_(name,registry));});correctedEquivalent=eeUnique_(correctedEquivalent);
  storedNames.forEach(function(name){if(structural[eeNorm_(name)]&&correctedEquivalent.indexOf(eeNorm_(name))===-1)reasons.push("STRUCTURAL_PRIMARY_ARTIST:"+eeNorm_(name));});
  keys.forEach(function(key){var normalized=eeNorm_(String(key).replace(/-/g," "));if(structural[normalized]&&correctedEquivalent.indexOf(normalized)===-1)reasons.push("STRUCTURAL_ARTIST_KEY:"+String(key));});
  var correctedArtists=correctedKeys.map(function(key){return (registry.artists||[]).filter(function(artist){return String(artist.slug)===String(key);})[0];}).filter(Boolean),reviewedIds=eeUnique_(correctedArtists.map(function(artist){return String(artist.appleArtistId||"");}).filter(Boolean));
  var storedIdentity=eeUnique_(storedNames.map(function(name){var equivalents=eeReadyAuditEquivalentNames_(name,registry);return equivalents.indexOf(eeNorm_(name))!==-1&&equivalents.some(function(value){return correctedEquivalent.indexOf(value)!==-1;})?equivalents.filter(function(value){return correctedEquivalent.indexOf(value)!==-1;})[0]:eeNorm_(name);})).sort(),correctedIdentity=eeUnique_(correctedNames.map(eeNorm_)).sort();if(correctedIdentity.length&&storedIdentity.join("|")!==correctedIdentity.join("|"))reasons.push("STORED_PRIMARY_ARTISTS_CONFLICT_WITH_CORRECTED_IDENTITY");
  if(keys.length===storedNames.length)keys.forEach(function(key,index){var artist=(registry.artists||[]).filter(function(value){return String(value.slug)===String(key);})[0];if(artist&&eeNorm_(artist.canonicalName)!==eeNorm_(storedNames[index]))reasons.push("ARTIST_KEY_CANONICAL_NAME_CONFLICT:"+String(key));});
  if(storedId&&reviewedIds.length&&reviewedIds.indexOf(storedId)===-1)reasons.push("APPLE_ARTIST_ID_CONFLICT:"+storedId+":"+reviewedIds.join(","));
  if(storedId&&sharedIds[storedId]&&sharedIds[storedId].length>1)advisories.push("APPLE_ID_SHARED_ACROSS_UNRELATED_ARTISTS:"+storedId);
  if(storedId==="452501576"&&!correctedNames.some(function(name){return eeNorm_(name)==="the sheepdogs";}))reasons.push("SHEEPDOGS_APPLE_ID_UNRELATED_IDENTITY");
  var items=[],conflicts=[];(payload.categories||[]).forEach(function(group){(group.items||[]).forEach(function(item){items.push(item);});});var creators=eeUnique_(items.map(function(item){return String(item.creator||"").trim();}).filter(Boolean)),itemAppleIds=eeUnique_(items.map(function(item){return String(item.appleArtistId||"");}).filter(Boolean)),allowed=eeReadyAuditRelationshipNames_(correctedArtists,registry);(payload.categories||[]).forEach(function(group){(group.items||[]).forEach(function(item){var check=eeReadyAuditItemCheck_(item,group.category,allowed,correctedNames);categoryReasons.push(String(group.category||"").toUpperCase()+":"+check.reason+":"+String(item.title||item.stableId||""));if(correctedNames.length&&!check.valid){reasons.push(String(group.category||"").toUpperCase()+"_RECOMMENDATION_RELEVANCE_CONFLICT:"+String(item.title||item.stableId||""));if(check.creatorConflict)conflicts.push(String(item.creator||""));}});});conflicts=eeUnique_(conflicts);
  if(reviewedIds.length&&itemAppleIds.length&&itemAppleIds.every(function(id){return reviewedIds.indexOf(id)===-1;}))reasons.push("ALL_RECOMMENDATION_APPLE_IDS_CONFLICT");
  if(creators.length&&conflicts.length===creators.length&&correctedNames.length)reasons.push("ALL_RECOMMENDATION_CREATORS_CONFLICT_WITH_PRIMARY");
  if(correctedNames.length)conflicts.forEach(function(creator){reasons.push("RECOMMENDATION_CREATOR_CONFLICT:"+creator);});
  conflicts.forEach(function(creator){var creatorNorm=eeNorm_(creator);if(correctedNames.some(function(name){var primary=eeNorm_(name);return primary&&creatorNorm&&(primary.indexOf(creatorNorm)!==-1||creatorNorm.indexOf(primary)!==-1);} ))reasons.push("LEXICAL_IDENTITY_COLLISION:"+creator);});
  if(Number(safetyContext.duplicateCount||0)>1)safetyBlocks.push("DUPLICATE_READY_ROW");if(!correctedNames.length||analysis.ambiguous||String(analysis.identityConfidence||"")==="LOW")safetyBlocks.push("CORRECTED_IDENTITY_NOT_TRUSTWORTHY");
  reasons=eeUnique_(reasons);advisories=eeUnique_(advisories);safetyBlocks=eeUnique_(safetyBlocks);categoryReasons=eeUnique_(categoryReasons);var objective=reasons.length>0,storedNorm=storedIdentity,correctedNorm=correctedIdentity,coherent=!!correctedNorm.length&&storedNorm.join("|")===correctedNorm.join("|")&&eeUnique_(keys.map(String)).sort().join("|")===eeUnique_(correctedKeys.map(String)).sort().join("|"),ambiguous=!objective&&(!correctedNames.length||(analysis.ambiguous&&!coherent)||safetyBlocks.indexOf("DUPLICATE_READY_ROW")!==-1);if(ambiguous)reasons.push(safetyBlocks.indexOf("DUPLICATE_READY_ROW")!==-1?"DUPLICATE_READY_ROW":(correctedNames.length?"ARTICLE_IDENTITY_AMBIGUOUS":"ARTICLE_IDENTITY_UNRESOLVED"));var categories={};(payload.categories||[]).forEach(function(group){categories[String(group.category||"")]=(group.items||[]).length;});var pending=correctedKeys.some(function(key){var state=artistStates[String(key)]||{};return state.enrichmentStatus!=="FULL";});var enrichment=!objective&&!ambiguous&&!!categories.LISTEN&&(!categories.WATCH||!categories.READ)&&pending;
  var classification=objective?"CONTAMINATED":ambiguous?"AMBIGUOUS":enrichment?"ENRICHMENT_CANDIDATE":"CLEAN",repairableReason=reasons.some(function(reason){return /^(?:STRUCTURAL_|STORED_PRIMARY_ARTISTS_CONFLICT|ARTIST_KEY_CANONICAL_NAME_CONFLICT|APPLE_ARTIST_ID_CONFLICT|SHEEPDOGS_APPLE_ID_UNRELATED_IDENTITY|ALL_RECOMMENDATION_)/.test(reason);}),autoSafe=classification==="CONTAMINATED"&&correctedNames.length>0&&!analysis.ambiguous&&!safetyBlocks.length&&repairableReason;
  return {classification:classification,postId:String(payload.postId||""),canonicalUrl:String(payload.canonicalUrl||""),title:String(subject.title||""),storedPrimaryArtists:storedNames,correctedPrimaryArtists:correctedNames,artistKeys:keys,storedAppleArtistId:storedId,recommendationCreators:creators,conflictingCreators:conflicts,reasons:reasons,categoryReasons:categoryReasons,safetyBlocks:safetyBlocks,advisories:advisories,replacementPreview:{status:"NOT_GENERATED_IN_READ_ONLY_AUDIT",primaryArtists:correctedNames,recommendationCreators:{LISTEN:[],WATCH:[],READ:[]},validation:"DEFERRED_TO_WRITE_MODE"},proposedAction:classification==="CONTAMINATED"?(autoSafe?"REGENERATE_REVIEWED_QUALITY":"MANUAL_REVIEW"):classification==="ENRICHMENT_CANDIDATE"?"CONTINUE_INCREMENTAL_ENRICHMENT":classification==="AMBIGUOUS"?"MANUAL_REVIEW":"NONE",automaticRepairSafe:autoSafe};
}

function eeReadyAuditReplacementPreview_(finding,existing,registry) {var preview={regenerationAttempted:true,regenerationSucceeded:false,correctedPrimaryArtists:[],artistKeys:[],canonicalIdentity:null,LISTEN:{creators:[],titles:[]},WATCH:{creators:[],titles:[]},READ:{creators:[],titles:[]},validationPassed:false,validationFailures:[],wouldWrite:false};try{EE_APPLE_READ_ONLY_GENERATION=true;var post=eeFetchPostById_(finding.postId),candidate=eeGeneratePayload_(post);candidate=eeMergeValidatedRepairItems_(candidate,existing,registry);preview.correctedPrimaryArtists=(candidate.subject||{}).primaryArtists||[];preview.artistKeys=(candidate.diagnostics||{}).artistKeys||[];preview.canonicalIdentity=candidate.identity||null;(candidate.categories||[]).forEach(function(group){var key=String(group.category||"").toUpperCase();if(!preview[key])return;(group.items||[]).forEach(function(item){preview[key].creators.push(String(item.creator||item.publisher||item.narrator||""));preview[key].titles.push(String(item.title||""));});});var failures=[];if(!eePayloadHasRecommendations_(candidate))failures.push("NO_RECOMMENDATIONS");var issues=eeReadyQualityIssues_(candidate,registry);if(issues.length)failures=failures.concat(issues);preview.validationFailures=eeUnique_(failures);preview.validationPassed=!preview.validationFailures.length;preview.regenerationSucceeded=true;preview.wouldWrite=preview.validationPassed;}catch(error){preview.validationFailures=[String(error&&error.code||error&&error.message||error)];}finally{EE_APPLE_READ_ONLY_GENERATION=false;}return preview;}

var EE_READY_AUDIT_PREVIEW=false,EE_APPLE_AUDIT_SKIP_PREVIEW=false;
function eeReadyAuditReplacementPreview_(finding,existing,registry) {var p={regenerationAttempted:true,regenerationSucceeded:false,correctedPrimaryArtists:[],LISTEN:{creators:[],titles:[]},WATCH:{creators:[],titles:[]},READ:{creators:[],titles:[]},validationPassed:false,validationFailures:[],wouldWrite:false};try{EE_READY_AUDIT_PREVIEW=true;var candidate=eeMergeValidatedRepairItems_(eeGeneratePayload_(eeFetchPostById_(finding.postId)),existing||{},registry);p.regenerationSucceeded=true;p.correctedPrimaryArtists=(candidate.subject||{}).primaryArtists||[];(candidate.categories||[]).forEach(function(g){var k=String(g.category||"").toUpperCase();if(!p[k])return;(g.items||[]).forEach(function(i){p[k].creators.push(String(i.creator||i.publisher||i.narrator||""));p[k].titles.push(String(i.title||""));});});p.validationFailures=eeReadyQualityIssues_(candidate,registry);p.validationPassed=!p.validationFailures.length;p.wouldWrite=p.validationPassed;}catch(e){p.validationFailures=[String(e&&e.code||e&&e.message||e)];}finally{EE_READY_AUDIT_PREVIEW=false;}return p;}
function eeRepairContaminatedReadyPayloadsBatch_(startIndex,maxCandidates) {startIndex=Math.max(0,Number(startIndex||0));maxCandidates=Math.max(1,Number(maxCandidates||10));EE_APPLE_AUDIT_SKIP_PREVIEW=true;var audit;try{audit=eeAuditContaminatedReadyPayloads();}finally{EE_APPLE_AUDIT_SKIP_PREVIEW=false;}var candidates=audit.findings.filter(function(value){return value.classification==="CONTAMINATED"&&value.automaticRepairSafe;}),slice=candidates.slice(startIndex,startIndex+maxCandidates),rows=[],wouldWrite=0,failures=0,registry=eeArtistRegistry_();slice.forEach(function(finding){var preview=eeReadyAuditReplacementPreview_(finding,finding,registry);rows.push({postId:finding.postId,title:finding.title,correctedPrimaryArtists:preview.correctedPrimaryArtists,LISTEN:preview.LISTEN,WATCH:preview.WATCH,READ:preview.READ,validationPassed:preview.validationPassed,wouldWrite:preview.wouldWrite,regenerationFailure:preview.validationFailures});if(preview.wouldWrite)wouldWrite+=1;if(!preview.regenerationSucceeded)failures+=1;});var result={startIndex:startIndex,processed:slice.length,nextIndex:startIndex+slice.length,hasMore:startIndex+slice.length<candidates.length,batchSize:maxCandidates,wouldWrite:wouldWrite,regenerationFailures:failures,rows:rows};console.log(JSON.stringify(result));return result;}
function eeRepairReadyPreviewBatch01(){return eeRepairContaminatedReadyPayloadsBatch_(0,10);}
function eeRepairReadyPreviewBatch02(){return eeRepairContaminatedReadyPayloadsBatch_(10,10);}
function eeRepairReadyPreviewBatch03(){return eeRepairContaminatedReadyPayloadsBatch_(20,10);}
function eeRepairReadyPreviewBatch04(){return eeRepairContaminatedReadyPayloadsBatch_(30,10);}
function eeRepairReadyPreviewBatch05(){return eeRepairContaminatedReadyPayloadsBatch_(40,10);}
function eeRepairReadyPreviewBatch06(){return eeRepairContaminatedReadyPayloadsBatch_(50,10);}
function eeRepairReadyPreviewBatch07(){return eeRepairContaminatedReadyPayloadsBatch_(60,10);}
function eeRepairReadyPreviewBatch08(){return eeRepairContaminatedReadyPayloadsBatch_(70,10);}
function eeRepairReadyPreviewBatch09(){return eeRepairContaminatedReadyPayloadsBatch_(80,10);}
function eeRepairReadyPreviewBatch10(){return eeRepairContaminatedReadyPayloadsBatch_(90,10);}
function eeRepairReadyPreviewBatch11(){return eeRepairContaminatedReadyPayloadsBatch_(100,10);}
function eeRepairReadyPreviewBatch12(){return eeRepairContaminatedReadyPayloadsBatch_(110,10);}
function eeRepairReadyPreviewBatch13(){return eeRepairContaminatedReadyPayloadsBatch_(120,10);}
function eeRepairReadyPreviewBatch14(){return eeRepairContaminatedReadyPayloadsBatch_(130,10);}
function eeRepairReadyPreviewBatch15(){return eeRepairContaminatedReadyPayloadsBatch_(140,10);}

function eeAuditContaminatedReadyPayloads() {
  var registry=eeArtistRegistry_(),payloadValues=eeReadOnlySheet_("Apple Payloads").getDataRange().getValues(),artistSheet=SpreadsheetApp.openById(eeAppleSettings_().spreadsheetId).getSheetByName("Apple Artists"),artistValues=artistSheet?artistSheet.getDataRange().getValues():[],decoded=[],shared={},artistStates={};
  for(var artistRow=1;artistRow<artistValues.length;artistRow+=1){var catalogue={};try{catalogue=artistValues[artistRow][8]?eeDecodePayloadCell_(String(artistValues[artistRow][8])):{};}catch(error){}artistStates[String(artistValues[artistRow][0])]={enrichmentStatus:String(((catalogue.enrichment||{}).status)||"")};}
  for(var row=1;row<payloadValues.length;row+=1){if(String(payloadValues[row][5])!=="READY")continue;try{var payload=eeDecodePayloadCell_(String(payloadValues[row][4]||""));decoded.push(payload);var id=String((payload.identity||{}).artistId||""),identitySignature=eeUnique_(((payload.subject||{}).primaryArtists||[]).map(eeNorm_)).sort().join("|");if(id&&identitySignature){shared[id]=shared[id]||[];if(shared[id].indexOf(identitySignature)===-1)shared[id].push(identitySignature);}}catch(error){}}
  var duplicateCounts={};decoded.forEach(function(payload){var key=String(payload.postId||"");if(!key)return;duplicateCounts[key]=(duplicateCounts[key]||0)+1;});var duplicatePosts={};Object.keys(duplicateCounts).forEach(function(key){if(duplicateCounts[key]>1)duplicatePosts[key]=true;});
  var findings=[],existingById={},counts={totalReadyScanned:decoded.length,CLEAN:0,CONTAMINATED:0,ENRICHMENT_CANDIDATE:0,AMBIGUOUS:0,automaticRepairSafe:0,duplicateReadyPosts:Object.keys(duplicatePosts).length,structuralContamination:0,appleIdContradictions:0,creatorMismatches:0,lexicalCollisions:0};decoded.forEach(function(payload){var key=String(payload.postId||""),finding=eeReadyAuditFinding_(payload,registry,shared,artistStates,{duplicateCount:duplicateCounts[key]||1});existingById[key]=payload;counts[finding.classification]+=1;if(finding.automaticRepairSafe){counts.automaticRepairSafe+=1;if(!EE_APPLE_AUDIT_SKIP_PREVIEW)finding.replacementPreview=eeReadyAuditReplacementPreview_(finding,payload,registry);}counts.creatorMismatches+=finding.conflictingCreators.length;finding.reasons.forEach(function(reason){if(reason.indexOf("STRUCTURAL_")===0)counts.structuralContamination+=1;if(reason.indexOf("APPLE_")===0||reason.indexOf("SHEEPDOGS_")===0)counts.appleIdContradictions+=1;if(reason.indexOf("LEXICAL_")===0)counts.lexicalCollisions+=1;});if(finding.classification!=="CLEAN")findings.push(finding);});var result={status:"OK",dryRun:true,counts:counts,repairSafeRows:findings.filter(function(value){return value.automaticRepairSafe;}),excludedFromAutoRepair:findings.filter(function(value){return value.classification==="CONTAMINATED"&&!value.automaticRepairSafe;}).map(function(value){return {postId:value.postId,title:value.title,canonicalUrl:value.canonicalUrl,safetyBlocks:value.safetyBlocks,reasons:value.reasons,categoryReasons:value.categoryReasons};}),findings:findings};console.log(JSON.stringify(result));return result;
}

function eeReadyQualityIssues_(payload,registry) {var finding=eeReadyAuditFinding_(payload,registry||eeArtistRegistry_(),{},{});return finding.classification==="CONTAMINATED"?finding.reasons:[];}

function eeQualityRepairItemValid_(item,allowedNames,allowedIds) {
  var creator=eeNorm_((item||{}).creator||""),artistId=String((item||{}).appleArtistId||"");
  return !!((artistId&&allowedIds.indexOf(artistId)!==-1)||(creator&&allowedNames.indexOf(creator)!==-1));
}

function eeMergeValidatedRepairItems_(candidate,existing,registry) {
  var names=((candidate.subject||{}).primaryArtists||[]).map(eeNorm_),primaryArtists=(registry.artists||[]).filter(function(artist){return names.indexOf(eeNorm_(artist.canonicalName))!==-1;}),allowed=eeReadyAuditRelationshipNames_(primaryArtists,registry),ids=[];
  (registry.artists||[]).forEach(function(artist){if(allowed.indexOf(eeNorm_(artist.canonicalName))!==-1&&artist.appleArtistId)ids.push(String(artist.appleArtistId));});
  if((candidate.identity||{}).artistId)ids.push(String(candidate.identity.artistId));ids=eeUnique_(ids);
  var groups={};(candidate.categories||[]).forEach(function(group){groups[group.category]=group;});
  (existing.categories||[]).forEach(function(group){(group.items||[]).forEach(function(item){if(!eeQualityRepairItemValid_(item,allowed,ids))return;var target=groups[group.category]||(groups[group.category]={category:group.category,items:[]}),key=String(item.stableId||item.url||item.title||"");if(!(target.items||[]).some(function(value){return String(value.stableId||value.url||value.title||"")===key;}))target.items.push(item);});});
  Object.keys(groups).forEach(function(category){groups[category].items.sort(function(a,b){return eePrimaryRecommendationRank_(a,names,[String((candidate.identity||{}).artistId||"")])-eePrimaryRecommendationRank_(b,names,[String((candidate.identity||{}).artistId||"")])||Number(b.relevanceScore||0)-Number(a.relevanceScore||0)||String(a.title||"").localeCompare(String(b.title||""));});});
  candidate.categories=["LISTEN","WATCH","READ"].map(function(category){return groups[category];}).filter(function(group){return group&&(group.items||[]).length;});return candidate;
}

function eePutReviewedQualityRepair_(post,payload) {
  var sheet=eePayloadSheet_(),stored=eeEncodePayloadCell_(payload),values=sheet.getDataRange().getValues(),target=values.length+1;
  for(var row=1;row<values.length;row+=1)if(String(values[row][0])===String(post.id)){target=row+1;break;}
  sheet.getRange(target,1,1,8).setValues([[String(post.id),post.url||"",new Date().toISOString(),payload.storefront||EE_APPLE_CONFIG.storefront,stored,"READY","QUALITY_REPAIR",0]]);CacheService.getScriptCache().remove("ee-apple-payload-"+String(post.id));return true;
}

function eeRepairContaminatedReadyPayloads(dryRun) {
  if(dryRun!==false)return eeAuditContaminatedReadyPayloads();var audit=eeAuditContaminatedReadyPayloads(),registry=eeArtistRegistry_(),sheet=eePayloadSheet_(),values=sheet.getDataRange().getValues(),existingById={},repaired=[];
  for(var row=1;row<values.length;row+=1){if(String(values[row][5])!=="READY")continue;try{existingById[String(values[row][0])]=eeDecodePayloadCell_(String(values[row][4]||""));}catch(error){}}
  audit.findings.forEach(function(finding){if(finding.classification!=="CONTAMINATED"||!finding.automaticRepairSafe)return;var existing=existingById[finding.postId];if(!existing)return;
    try{var post=eeFetchPostById_(finding.postId),candidate=eeGeneratePayload_(post);candidate=eeMergeValidatedRepairItems_(candidate,existing,registry);if(!eePayloadHasRecommendations_(candidate))return;if(eeReadyQualityIssues_(candidate,registry).length)return;eePutReviewedQualityRepair_(post,candidate);repaired.push(finding.postId);}catch(error){console.log(JSON.stringify({qualityRepairPostId:finding.postId,status:"PRESERVED_READY",error:String(error&&error.code||error&&error.message||error)}));}
  });
  var result={status:"OK",dryRun:false,counts:audit.counts,findings:audit.findings,repaired:repaired};console.log(JSON.stringify(result));return result;
}

function eePrimaryArtistIdentityPayload_(artist,post) {
  var settings=eeAppleSettings_();
  var analysis={primaryArtists:[artist.canonicalName],people:[],associatedPeople:[],existingAppleArtistIds:artist.appleArtistId?[String(artist.appleArtistId)]:[],relationshipGraph:{nodes:[],edges:[]}};
  var query=eePrimaryLookupQuery_(analysis,settings.storefront,"LISTEN","album"),queryDiagnostic=eeDiscoveryDiagnosticQuery_(query),response=eeAppleSearch_(query),results=response.results||[],map={};
  eeDiscoveryDiagnosticCandidates_(queryDiagnostic,response);
  results.forEach(function(raw){
    if(eeAddCandidateToMap_(map,raw,query,analysis))eeDiscoveryDiagnosticDecision_(queryDiagnostic,true,"QUALIFYING_RELATIONSHIP");
    else eeDiscoveryDiagnosticDecision_(queryDiagnostic,false,"NO_QUALIFYING_RELATIONSHIP");
  });
  var identity=eeResolveIdentity_(analysis,results),items=Object.keys(map).map(function(key){return map[key];});
  if(identity.level==="HIGH"&&identity.artistId)items=items.filter(function(item){return !item.appleArtistId||String(item.appleArtistId)===String(identity.artistId);});
  items.sort(function(a,b){return Number(b.relevanceScore||0)-Number(a.relevanceScore||0)||String(a.title||"").localeCompare(String(b.title||""));});
  return {schemaVersion:1,generationVersion:EE_APPLE_CONFIG.generationVersion,identity:identity,categories:items.length?[{category:"LISTEN",items:items}]:[],diagnostics:{fastPrimaryIdentity:true,searchIntents:["LISTEN:album:"+artist.canonicalName],rawResultCount:results.length}};
}

var EE_APPLE_ENRICHMENT_QUERIES_PER_RUN=3;
function eeEnrichmentQueryKey_(query){return [query.category,query.media,query.entity,eeNorm_(query.term||""),String(query.storefront||"").toUpperCase()].join("|");}
function eeEnrichmentTransient_(error){var value=String((error&&error.code)||(error&&error.message)||error||"");return !!(error&&error.retryable)||/HTTP_(?:403|429|5\d\d)|HEADROOM|COOLDOWN|network|timed?\s*out|connection|service unavailable|fetch failed/i.test(value);}

function eeIncrementalResolvedEnrichment_(artist,post,existing) {
  var analysis=eeArticleAnalysis_(post),settings=eeAppleSettings_(),plan=eeSearchPlan_(analysis,settings.storefront);
  analysis.existingAppleArtistIds=[String(existing.appleArtistId)];
  if((analysis.primaryArtists||[]).length>1){var primarySet={};analysis.primaryArtists.forEach(function(name){primarySet[eeNorm_(name)]=true;});plan=plan.filter(function(query){return query.intent==="ARTIST"&&primarySet[eeNorm_(query.term||"")];});}
  var prior=(existing.catalogue||{}).enrichment||{},completed={},map={};
  (prior.completedQueries||[]).forEach(function(key){completed[String(key)]=true;});
  ((existing.catalogue||{}).categories||[]).forEach(function(group){(group.items||[]).forEach(function(item){map[String(item.category||group.category)+":"+String(item.stableId||item.url||item.title)]=item;});});
  var attempted=0,lastError="";
  for(var index=0;index<plan.length&&attempted<EE_APPLE_ENRICHMENT_QUERIES_PER_RUN;index+=1){
    var query=plan[index],key=eeEnrichmentQueryKey_(query);if(completed[key])continue;
    var queryDiagnostic=eeDiscoveryDiagnosticQuery_(query);
    try{
      var response=eeAppleSearch_(query);eeDiscoveryDiagnosticCandidates_(queryDiagnostic,response);
      (response.results||[]).forEach(function(raw){if(eeAddCandidateToMap_(map,raw,query,analysis))eeDiscoveryDiagnosticDecision_(queryDiagnostic,true,"QUALIFYING_RELATIONSHIP");else eeDiscoveryDiagnosticDecision_(queryDiagnostic,false,"NO_QUALIFYING_RELATIONSHIP");});
      completed[key]=true;attempted+=1;
    }catch(error){if(!eeEnrichmentTransient_(error))throw error;lastError=String(error.code||error.message||error);break;}
  }
  var completedKeys=Object.keys(completed),remaining=plan.filter(function(query){return !completed[eeEnrichmentQueryKey_(query)];}),groups={LISTEN:[],WATCH:[],READ:[]};
  Object.keys(map).forEach(function(key){var item=map[key];if(groups[item.category])groups[item.category].push(item);});
  var categories=[];["LISTEN","WATCH","READ"].forEach(function(category){groups[category].sort(function(a,b){return eePrimaryRecommendationRank_(a,[artist.canonicalName],[existing.appleArtistId])-eePrimaryRecommendationRank_(b,[artist.canonicalName],[existing.appleArtistId])||Number(b.relevanceScore||0)-Number(a.relevanceScore||0)||String(a.title||"").localeCompare(String(b.title||""));});if(groups[category].length)categories.push({category:category,items:groups[category]});});
  var state={status:remaining.length?"PENDING":"FINALIZE",completedQueries:completedKeys,totalQueries:plan.length,pendingQueries:remaining.length,lastError:lastError};
  eeDiscoveryDiagnosticEnrichment_(state);
  return {readyForFinalization:!remaining.length&&!lastError,categories:categories,enrichment:state,lastError:lastError};
}

function eeDiscoverArtistCatalogue_(artist,post,forceRefresh) {
  var diagnostic=eeDiscoveryDiagnosticStart_(artist);
  var lease="CATALOGUE_"+String(artist.slug||"").replace(/[^A-Za-z0-9_-]/g,"_");
  if(!eeAcquireWorkerLease_(lease,360000)){var busy=new Error("ARTIST_DISCOVERY_BUSY");busy.code="ARTIST_DISCOVERY_BUSY";busy.retryable=true;eeDiscoveryDiagnosticFinish_(diagnostic,"RETRY_LATER",busy.code,busy);throw busy;}
  try{
    var existing=eeGetArtistCatalogue_(artist.slug);if(existing&&existing.appleArtistId&&existing.status!=="RESOLVED"){existing.status="RESOLVED";existing.identityConfidence="HIGH";}
    if(existing&&["UNRESOLVED","DEFERRED"].indexOf(existing.status)===-1&&!forceRefresh){eeDiscoveryDiagnosticFinish_(diagnostic,existing.status,"EXISTING_CATALOGUE",null);return existing;}
    if(forceRefresh&&existing&&existing.status==="RESOLVED"&&existing.appleArtistId){
      var progress=eeIncrementalResolvedEnrichment_(artist,post,existing);
      if(!progress.readyForFinalization){
        var pendingRecord={artistKey:artist.slug,canonicalName:artist.canonicalName,appleArtistId:existing.appleArtistId,musicBrainzId:existing.musicBrainzId||artist.musicBrainzId||"",identityConfidence:existing.identityConfidence||"HIGH",status:"RESOLVED",error:progress.lastError,categories:progress.categories,representativePostId:String(post.id),staleAfter:new Date().toISOString(),enrichment:progress.enrichment};
        eePutArtistCatalogue_(pendingRecord);pendingRecord.catalogue={schemaVersion:1,generationVersion:EE_APPLE_CONFIG.generationVersion,artistKey:pendingRecord.artistKey,canonicalName:pendingRecord.canonicalName,categories:pendingRecord.categories,enrichment:pendingRecord.enrichment};eeDiscoveryDiagnosticFinish_(diagnostic,"RESOLVED","ENRICHMENT_PENDING",progress.lastError?{code:progress.lastError}:null);return pendingRecord;
      }
    }
    var legacy=forceRefresh?eeGeneratePayloadLegacy_(post):eePrimaryArtistIdentityPayload_(artist,post),fastResolved=!forceRefresh&&String((legacy.identity||{}).level)==="HIGH"&&!!(legacy.identity||{}).artistId;
    if(!forceRefresh&&!fastResolved)legacy=eeGeneratePayloadLegacy_(post);
    var identity=legacy.identity||{};
    var categories=(legacy.categories||[]).map(function(group){return {category:group.category,items:(group.items||[]).filter(function(item){return !item.creator||eeNorm_(item.creator)===eeNorm_(artist.canonicalName)||group.category!=="LISTEN";})};}).filter(function(group){return group.items.length;});
    var confidence=String(identity.level||"LOW"),appleArtistId=identity.artistId||artist.appleArtistId||"",status=(appleArtistId||confidence==="HIGH")?"RESOLVED":confidence==="MODERATE"?"AMBIGUOUS":"ERROR",errorReason=status==="ERROR"?"APPLE_ARTIST_DISCOVERY_EXHAUSTED":"";
    if(status==="ERROR")categories=[];
    var enrichment=status==="RESOLVED"?{status:fastResolved?"PENDING":"FULL",completedQueries:[],totalQueries:0,pendingQueries:fastResolved?1:0,lastError:""}:null;
    var record={artistKey:artist.slug,canonicalName:artist.canonicalName,appleArtistId:appleArtistId,musicBrainzId:artist.musicBrainzId||"",identityConfidence:confidence,status:status,error:errorReason,categories:categories,representativePostId:String(post.id),staleAfter:fastResolved?new Date().toISOString():"",enrichment:enrichment};
    eePutArtistCatalogue_(record);var properties=PropertiesService.getScriptProperties();properties.setProperty("EE_APPLE_CATALOGUE_GENERATION_COUNT",String(Number(properties.getProperty("EE_APPLE_CATALOGUE_GENERATION_COUNT")||0)+1));record.catalogue={schemaVersion:1,generationVersion:EE_APPLE_CONFIG.generationVersion,artistKey:record.artistKey,canonicalName:record.canonicalName,categories:record.categories};if(enrichment)record.catalogue.enrichment=enrichment;eeDiscoveryDiagnosticEnrichment_(enrichment);eeDiscoveryDiagnosticFinish_(diagnostic,status,errorReason||(fastResolved?"PRIMARY_IDENTITY_CONFIDENT":status==="RESOLVED"?"CONFIDENT_MATCH":"PLAUSIBLE_MATCH"),null);return record;
  }catch(error){
    if(forceRefresh&&existing&&existing.status==="RESOLVED"&&existing.appleArtistId&&eeEnrichmentTransient_(error)){
      var transientReason=String(error.code||error.message||error),preservedCategories=(progress&&progress.categories)||((existing.catalogue||{}).categories||[]),preservedState=(progress&&progress.enrichment)||(existing.catalogue||{}).enrichment||{};
      preservedState={status:"FINALIZE_PENDING",completedQueries:preservedState.completedQueries||[],totalQueries:Number(preservedState.totalQueries||0),pendingQueries:Number(preservedState.pendingQueries||0),lastError:transientReason};eeDiscoveryDiagnosticEnrichment_(preservedState);
      var preserved={artistKey:artist.slug,canonicalName:artist.canonicalName,appleArtistId:existing.appleArtistId,musicBrainzId:existing.musicBrainzId||artist.musicBrainzId||"",identityConfidence:existing.identityConfidence||"HIGH",status:"RESOLVED",error:transientReason,categories:preservedCategories,representativePostId:String(post.id),staleAfter:new Date().toISOString(),enrichment:preservedState};
      eePutArtistCatalogue_(preserved);preserved.catalogue={schemaVersion:1,generationVersion:EE_APPLE_CONFIG.generationVersion,artistKey:preserved.artistKey,canonicalName:preserved.canonicalName,categories:preserved.categories,enrichment:preserved.enrichment};eeDiscoveryDiagnosticFinish_(diagnostic,"RESOLVED","ENRICHMENT_PENDING",error);return preserved;
    }
    eeDiscoveryDiagnosticFinish_(diagnostic,error&&error.retryable?"RETRY_LATER":"ERROR",String((error&&error.code)||(error&&error.message)||"DISCOVERY_ERROR"),error);throw error;
  }finally{eeReleaseWorkerLease_(lease);}
}

function eeGeneratePayload_(post) {
  var registry=eeArtistRegistry_(),analysis=eeFastArticleIdentity_(post,registry);eePutArticleIdentity_(analysis);
  if(!analysis.primaryArtistKeys.length)return eeAssemblePayloadFromCatalogues_(post,analysis,[]);
  var catalogues=[];
  analysis.primaryArtistKeys.forEach(function(key,index){var artist=registry.artists.filter(function(value){return value.slug===key;})[0]||{canonicalName:analysis.primaryArtists[index],slug:key,aliases:[],ambiguityClass:"provisional"},record=eeGetArtistCatalogue_(key);if((!record||record.status==="UNRESOLVED")&&!catalogues.length)record=eeDiscoverArtistCatalogue_(artist,post);if(record&&record.status==="RESOLVED"&&eePayloadHasRecommendations_(record.catalogue))catalogues.push(record);});
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
    eeSetExecutionDeadline_(Math.min(EE_APPLE_EXECUTION_DEADLINE||Date.now()+180000,Date.now()+180000));
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
        if(eeEnrichmentTransient_(error)){
          var transientError=String(error.code||error.message||error),retryCount=Math.max(0,Number(values[row][13]||0))+1,retryAfter="";
          if(retryCount<EE_APPLE_ARTIST_TRANSIENT_RETRY_LIMIT){
            eePutArtistCatalogue_({artistKey:artistKey,canonicalName:canonicalName,identityConfidence:"UNRESOLVED",status:"UNRESOLVED",representativePostId:representativePostId,error:transientError,categories:[],transientRetryCount:retryCount,lastTransientError:transientError});
            properties.setProperty("EE_APPLE_ARTIST_DISCOVERY_INDEX",String(row));
            console.log(JSON.stringify({artistKey:artistKey,canonicalName:canonicalName,transientError:transientError,retryCount:retryCount,retryLimit:EE_APPLE_ARTIST_TRANSIENT_RETRY_LIMIT,cursor:row}));
            return {status:"RETRY_LATER",artistKey:artistKey,error:transientError,retryCount:retryCount,retryLimit:EE_APPLE_ARTIST_TRANSIENT_RETRY_LIMIT};
          }
          if(eeArtistClearCanonical_(artist)){
            retryAfter=new Date(Date.now()+EE_APPLE_CLEAR_IDENTITY_RETRY_MS).toISOString();
            eePutArtistCatalogue_({artistKey:artistKey,canonicalName:canonicalName,identityConfidence:"UNRESOLVED",status:"UNRESOLVED",representativePostId:representativePostId,error:transientError,categories:[],transientRetryCount:retryCount,lastTransientError:transientError,retryAfter:retryAfter});
            properties.setProperty("EE_APPLE_ARTIST_DISCOVERY_INDEX",String(row+1));
            console.log(JSON.stringify({artistKey:artistKey,canonicalName:canonicalName,terminalStatus:"IDENTITY_RETRY_PENDING",lastTransientError:transientError,retryCount:retryCount,retryAfter:retryAfter,nextCursor:row+1}));
            continue;
          }
          retryAfter=new Date(Date.now()+EE_APPLE_ARTIST_DEFERRED_RETRY_MS).toISOString();
          eePutArtistCatalogue_({artistKey:artistKey,canonicalName:canonicalName,identityConfidence:"DEFERRED",status:"DEFERRED",representativePostId:representativePostId,error:transientError,categories:[],transientRetryCount:retryCount,lastTransientError:transientError,retryAfter:retryAfter});
          properties.setProperty("EE_APPLE_ARTIST_DISCOVERY_INDEX",String(row+1));
          console.log(JSON.stringify({artistKey:artistKey,canonicalName:canonicalName,terminalStatus:"DEFERRED",lastTransientError:transientError,retryCount:retryCount,retryAfter:retryAfter,nextCursor:row+1}));
          continue;
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
  try{var sheet=eeArtistCatalogueSheet_(),values=sheet.getDataRange().getValues(),properties=PropertiesService.getScriptProperties(),cursor=Math.max(1,Number(properties.getProperty("EE_APPLE_STALE_REFRESH_INDEX")||1));eeSetExecutionDeadline_(Math.min(EE_APPLE_EXECUTION_DEADLINE||Date.now()+180000,Date.now()+180000));
  for(var row=cursor;row<values.length;row+=1){
    var status=String(values[row][7]||""),appleArtistId=String(values[row][4]||""),isVerifiedResolved=!!appleArtistId&&(status==="RESOLVED"||status==="DEFERRED"||String(values[row][6]||"")==="HIGH"),isDeferred=status==="DEFERRED"&&!isVerifiedResolved,storedCatalogue={};try{storedCatalogue=values[row][8]?eeDecodePayloadCell_(String(values[row][8])):{};}catch(decodeError){}var enrichmentStatus=String(((storedCatalogue.enrichment||{}).status)||""),isEnrichmentPending=isVerifiedResolved&&enrichmentStatus!=="FULL",isStale=isVerifiedResolved&&(isEnrichmentPending||(values[row][10]&&Date.parse(String(values[row][10]))<=Date.now())),retryAfter=String(values[row][15]||"");
    var artistKey=String(values[row][0]),canonicalName=String(values[row][1]),representativePostId=String(values[row][11]||""),registry=eeArtistRegistry_(),artist=registry.artists.filter(function(value){return value.slug===artistKey;})[0]||{slug:artistKey,canonicalName:canonicalName,aliases:[],ambiguityClass:"provisional"};
    var isClearIdentityRetry=status==="UNRESOLVED"&&eeArtistClearCanonical_(artist)&&!!retryAfter&&Date.parse(retryAfter)<=Date.now();
    if(!isStale&&!isClearIdentityRetry&&(!isDeferred||!retryAfter||Date.parse(retryAfter)>Date.now())){properties.setProperty("EE_APPLE_STALE_REFRESH_INDEX",String(row+1));continue;}
    try{
      var post=eeFetchPostById_(representativePostId),catalogue=eeDiscoverArtistCatalogue_(artist,post,isVerifiedResolved);properties.setProperty("EE_APPLE_ASSEMBLY_INDEX","1");
      properties.setProperty("EE_APPLE_STALE_REFRESH_INDEX",String(row+1));
      return {status:isVerifiedResolved?"ENRICHMENT_REFRESHED":isDeferred?"DEFERRED_RETRIED":"IDENTITY_RETRIED",artistKey:artist.slug,terminalStatus:String(catalogue&&catalogue.status||""),cursor:row+1};
    }catch(error){
      var errorReason=String(error&&error.code||error&&error.message||error);
      if(eeEnrichmentTransient_(error)){
        if(isVerifiedResolved){
          var priorCatalogue={};try{priorCatalogue=values[row][8]?eeDecodePayloadCell_(values[row][8]):{};}catch(decodeError){}var priorEnrichment=priorCatalogue.enrichment||{status:"PENDING",completedQueries:[],totalQueries:0,pendingQueries:1};priorEnrichment.status="PENDING";priorEnrichment.lastError=errorReason;
          eePutArtistCatalogue_({artistKey:artistKey,canonicalName:canonicalName,appleArtistId:appleArtistId,musicBrainzId:String(values[row][5]||""),identityConfidence:"HIGH",status:"RESOLVED",representativePostId:representativePostId,error:errorReason,categories:priorCatalogue.categories||[],staleAfter:new Date().toISOString(),enrichment:priorEnrichment,lastTransientError:errorReason});
          properties.setProperty("EE_APPLE_STALE_REFRESH_INDEX",String(row+1));return {status:"ENRICHMENT_PENDING",artistKey:artist.slug,error:errorReason,terminalStatus:"RESOLVED",cursor:row+1};
        }
        var retryCount=Math.max(0,Number(values[row][13]||0))+1,nextRetryAfter=new Date(Date.now()+EE_APPLE_ARTIST_DEFERRED_RETRY_MS).toISOString();
        if(eeArtistClearCanonical_(artist)){nextRetryAfter=new Date(Date.now()+EE_APPLE_CLEAR_IDENTITY_RETRY_MS).toISOString();eePutArtistCatalogue_({artistKey:artistKey,canonicalName:canonicalName,identityConfidence:"UNRESOLVED",status:"UNRESOLVED",representativePostId:representativePostId,error:errorReason,categories:[],transientRetryCount:retryCount,lastTransientError:errorReason,retryAfter:nextRetryAfter});properties.setProperty("EE_APPLE_STALE_REFRESH_INDEX",String(row+1));return {status:"IDENTITY_RETRY_PENDING",artistKey:artist.slug,error:errorReason,retryCount:retryCount,retryAfter:nextRetryAfter,cursor:row+1};}
        eePutArtistCatalogue_({artistKey:artistKey,canonicalName:canonicalName,identityConfidence:"DEFERRED",status:"DEFERRED",representativePostId:representativePostId,error:errorReason,categories:[],transientRetryCount:retryCount,lastTransientError:errorReason,retryAfter:nextRetryAfter});
        properties.setProperty("EE_APPLE_STALE_REFRESH_INDEX",String(row+1));
        console.log(JSON.stringify({artistKey:artistKey,canonicalName:canonicalName,terminalStatus:"DEFERRED",lastTransientError:errorReason,retryCount:retryCount,retryAfter:nextRetryAfter,nextCursor:row+1}));
        return {status:"DEFERRED",artistKey:artist.slug,error:errorReason,retryCount:retryCount,retryAfter:nextRetryAfter,cursor:row+1};
      }
      eePutArtistCatalogue_({artistKey:artistKey,canonicalName:canonicalName,identityConfidence:"ERROR",status:"ERROR",representativePostId:representativePostId,error:errorReason,categories:[]});
      properties.setProperty("EE_APPLE_STALE_REFRESH_INDEX",String(row+1));
      return {status:"ERROR",artistKey:artist.slug,error:errorReason,cursor:row+1};
    }
  }
  properties.setProperty("EE_APPLE_STALE_REFRESH_INDEX","1");return {status:"COMPLETE",cursor:1};}finally{eeClearExecutionDeadline_();eeReleaseWorkerLease_("STALE_REFRESH");}
}

var EE_APPLE_ASSEMBLY_ROW_LIMIT=25;
var EE_APPLE_ASSEMBLY_TIME_LIMIT_MS=150000;
function eeAssembleArticlePayloadsWorker() {
  if(!eeAcquireWorkerLease_("ASSEMBLY",240000))return {status:"BUSY"};
  var started=Date.now();
  try{
    var properties=PropertiesService.getScriptProperties(),sheet=eeArticleIdentitySheet_(),values=sheet.getDataRange().getValues(),cursor=Math.max(1,Number(properties.getProperty("EE_APPLE_ASSEMBLY_INDEX")||1));
    var totals={status:"OK",processed:0,readyWritten:0,readyPreserved:0,skippedNoSubject:0,skippedUnresolved:0,skippedNoProducts:0,nextCursor:cursor,elapsedMs:0};
    for(var row=cursor;row<values.length&&totals.processed<EE_APPLE_ASSEMBLY_ROW_LIMIT&&Date.now()-started<EE_APPLE_ASSEMBLY_TIME_LIMIT_MS;row+=1){
      var nextCursor=row+1;totals.processed+=1;
      var keys=JSON.parse(String(values[row][4]||"[]"));if(!keys.length){totals.skippedNoSubject+=1;properties.setProperty("EE_APPLE_ASSEMBLY_INDEX",String(nextCursor));totals.nextCursor=nextCursor;continue;}
      var records=keys.map(eeGetArtistCatalogue_).filter(Boolean),resolved=records.filter(function(record){return record.status==="RESOLVED";});if(!resolved.length){totals.skippedUnresolved+=1;properties.setProperty("EE_APPLE_ASSEMBLY_INDEX",String(nextCursor));totals.nextCursor=nextCursor;continue;}
      var catalogues=resolved.filter(function(record){return eePayloadHasRecommendations_(record.catalogue);});if(!catalogues.length){totals.skippedNoProducts+=1;properties.setProperty("EE_APPLE_ASSEMBLY_INDEX",String(nextCursor));totals.nextCursor=nextCursor;continue;}
      var post=eeFetchPostById_(String(values[row][0])),analysis={primaryArtistKeys:keys,primaryArtists:JSON.parse(String(values[row][5]||"[]")),people:[],identityConfidence:String(values[row][6]),articleType:String(values[row][9])},payload=eeAssemblePayloadFromCatalogues_(post,analysis,catalogues);if(!eePayloadHasRecommendations_(payload)){totals.skippedNoProducts+=1;properties.setProperty("EE_APPLE_ASSEMBLY_INDEX",String(nextCursor));totals.nextCursor=nextCursor;continue;}
      var existing=eeGetPayload_(String(values[row][0])),preserved=eePayloadHasRecommendations_(existing)&&!eePayloadAtLeastAsUseful_(payload,existing);eePutPayload_(post,payload,"READY","",0);if(preserved)totals.readyPreserved+=1;else totals.readyWritten+=1;
      properties.setProperty("EE_APPLE_ASSEMBLY_INDEX",String(nextCursor));totals.nextCursor=nextCursor;
    }
    totals.elapsedMs=Date.now()-started;console.log(JSON.stringify(totals));return totals;
  }finally{eeReleaseWorkerLease_("ASSEMBLY");}
}

function eeSeedArtistCataloguesFromGeneration2() {
  var values=eePayloadSheet_().getDataRange().getValues(),registry=eeArtistRegistry_(),seeded=0;
  for(var row=1;row<values.length;row+=1){if(String(values[row][5])!=="READY")continue;var payload=eeDecodePayloadCell_(values[row][4]);if(!eePayloadHasRecommendations_(payload)||Number(payload.generationVersion)!==2)continue;var names=((payload.subject||{}).primaryArtists||[]);if(names.length!==1)continue;var artist=registry.artists.filter(function(value){return eeNorm_(value.canonicalName)===eeNorm_(names[0]);})[0];if(!artist||eeGetArtistCatalogue_(artist.slug))continue;var identity=payload.identity||{};if(identity.level!=="HIGH")continue;eePutArtistCatalogue_({artistKey:artist.slug,canonicalName:artist.canonicalName,appleArtistId:identity.artistId||"",identityConfidence:"HIGH",status:"RESOLVED",categories:payload.categories,representativePostId:String(payload.postId)});seeded+=1;}
  return {status:"OK",seeded:seeded};
}

function eeArchitectureStatus() {
  var properties=PropertiesService.getScriptProperties(),identity=eeArticleIdentitySheet_().getDataRange().getValues(),artists=eeArtistCatalogueSheet_().getDataRange().getValues(),payloads=eePayloadSheet_().getDataRange().getValues(),result={postsAnalyzed:Math.max(0,identity.length-1),canonicalArtists:Math.max(0,artists.length-1),verifiedAppleIds:0,unresolvedArtists:0,ambiguousArtists:0,deferredArtists:0,resolvedFullyEnriched:0,resolvedEnrichmentPending:0,partiallyEnrichedArtists:0,articlesWaitingOnEnrichment:0,artistTransientRetries:0,staleArtists:0,payloadStatus:{READY:0,EMPTY:{},ERROR:{}},appleCalls:Number(properties.getProperty("EE_APPLE_CALL_COUNT")||0),appleCacheHits:Number(properties.getProperty("EE_APPLE_CACHE_HIT_COUNT")||0),catalogueGenerations:Number(properties.getProperty("EE_APPLE_CATALOGUE_GENERATION_COUNT")||0),identityCursor:Number(properties.getProperty("EE_APPLE_IDENTITY_INDEX")||1),artistDiscoveryCursor:Number(properties.getProperty("EE_APPLE_ARTIST_DISCOVERY_INDEX")||1),assemblyCursor:Number(properties.getProperty("EE_APPLE_ASSEMBLY_INDEX")||1),staleRefreshCursor:Number(properties.getProperty("EE_APPLE_STALE_REFRESH_INDEX")||1),cooldownUntil:properties.getProperty("EE_APPLE_COOLDOWN_UNTIL")||null,mostRecentTransientFailure:properties.getProperty("EE_APPLE_LAST_TRANSIENT_FAILURE")||null},pendingArtistKeys={};
  for(var row=1;row<artists.length;row+=1){var rowStatus=String(artists[row][7]||""),rowAppleId=String(artists[row][4]||""),rowStale=!!artists[row][10]&&Date.parse(String(artists[row][10]))<=Date.now(),verifiedResolved=!!rowAppleId&&(rowStatus==="RESOLVED"||rowStatus==="DEFERRED"||String(artists[row][6]||"")==="HIGH");if(rowAppleId)result.verifiedAppleIds+=1;if(rowStatus==="UNRESOLVED")result.unresolvedArtists+=1;if(rowStatus==="AMBIGUOUS")result.ambiguousArtists+=1;if(rowStatus==="DEFERRED"&&!verifiedResolved)result.deferredArtists+=1;if(verifiedResolved){var catalogue={};try{catalogue=artists[row][8]?eeDecodePayloadCell_(artists[row][8]):{};}catch(error){}var enrichment=(catalogue.enrichment||{}).status||"";if(enrichment==="FULL")result.resolvedFullyEnriched+=1;else{result.resolvedEnrichmentPending+=1;pendingArtistKeys[String(artists[row][0])]=true;if((catalogue.categories||[]).some(function(group){return (group.items||[]).length;}))result.partiallyEnrichedArtists+=1;}}result.artistTransientRetries+=Math.max(0,Number(artists[row][13]||0));if(rowStale)result.staleArtists+=1;}
  var readyPayloadPosts={};for(var payloadRow=1;payloadRow<payloads.length;payloadRow+=1){if(String(payloads[payloadRow][5]||"")==="READY"&&eeStoredPayloadHasRecommendations_(payloads[payloadRow][4]))readyPayloadPosts[String(payloads[payloadRow][0])]=true;}
  for(var identityRow=1;identityRow<identity.length;identityRow+=1){var identityKeys=[];try{identityKeys=JSON.parse(String(identity[identityRow][4]||"[]"));}catch(error){}if(!readyPayloadPosts[String(identity[identityRow][0])]&&identityKeys.some(function(key){return pendingArtistKeys[String(key)];}))result.articlesWaitingOnEnrichment+=1;}
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
        "  } catch(error) {\n\n    try {\n      eePutPayload_(",
        "  } catch(error) {\n\n    if (error && (error.retryable || eeEnrichmentTransient_(error))) throw error;\n\n    try {\n      eePutPayload_(",
        "transient article failure preservation",
    )
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
        "function eePutPayload_(post, payload, status, error, retryCount) {\n  var sheet = eePayloadSheet_();",
        "function eePutPayload_(post, payload, status, error, retryCount) {\n"
        "  var existing=eeGetPayload_(post.id);\n"
        "  if(eePayloadHasRecommendations_(existing)&&(status!==\"READY\"||!eePayloadAtLeastAsUseful_(payload,existing)))return false;\n"
        "  var sheet = eePayloadSheet_();",
        "last-known-good READY protection",
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
    code = replace_once(
        code,
        '  analysis.relationshipGraph.nodes.filter(function(node){return node.weight>=76;}).forEach(function(node){add(node,"LISTEN","music","album");add(node,"WATCH","music","musicVideo");add(node,"READ","ebook","ebook");add(node,"READ","audiobook","audiobook");});',
        '  analysis.relationshipGraph.nodes.filter(function(node){return node.weight>=76;}).forEach(function(node){add(node,"LISTEN","music","album");if(node.normalizedName===primary){add(node,"WATCH","music","musicVideo");add(node,"READ","ebook","ebook");add(node,"READ","audiobook","audiobook");}});',
        "primary-only WATCH and READ plan",
    )
    code = replace_once(
        code,
        '  var exactPrimaryCreator=eeNorm_(creator)===primary;\n  var relationshipMatch=query.relationshipWeight&&(',
        '  var exactPrimaryCreator=eeNorm_(creator)===primary;\n'
        '  if((query.category==="WATCH"||query.category==="READ")&&eeNorm_(query.term||"")!==primary)return null;\n'
        '  var verifiedArtistId=String((analysis.existingAppleArtistIds||[])[0]||""),candidateArtistId=String(raw.artistId||raw.collectionArtistId||"");\n'
        '  if(verifiedArtistId&&candidateArtistId&&exactPrimaryCreator&&(query.category==="LISTEN"||query.category==="WATCH")&&candidateArtistId!==verifiedArtistId)return null;\n'
        '  var relationshipMatch=query.relationshipWeight&&(',
        "primary-only WATCH and READ candidates",
    )
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
        '  plan.forEach(function(query){\n    var response=eeAppleSearch_(query);',
        '  plan.forEach(function(query){\n    var queryDiagnostic=eeDiscoveryDiagnosticQuery_(query);\n    var response=eeAppleSearch_(query);\n    eeDiscoveryDiagnosticCandidates_(queryDiagnostic,response);',
        "per-artist query diagnostics",
    )
    code = replace_once(
        code,
        '      if(eeAddCandidateToMap_(map,raw,query,analysis))diagnostics.acceptedCount+=1;\n      else{diagnostics.rejectedCount+=1;diagnostics.relationshipRejectedCount+=1;diagnostics.rejectionReasons.NO_QUALIFYING_RELATIONSHIP=(diagnostics.rejectionReasons.NO_QUALIFYING_RELATIONSHIP||0)+1;}',
        '      if(eeAddCandidateToMap_(map,raw,query,analysis)){diagnostics.acceptedCount+=1;eeDiscoveryDiagnosticDecision_(queryDiagnostic,true,"QUALIFYING_RELATIONSHIP");}\n      else{diagnostics.rejectedCount+=1;diagnostics.relationshipRejectedCount+=1;diagnostics.rejectionReasons.NO_QUALIFYING_RELATIONSHIP=(diagnostics.rejectionReasons.NO_QUALIFYING_RELATIONSHIP||0)+1;eeDiscoveryDiagnosticDecision_(queryDiagnostic,false,"NO_QUALIFYING_RELATIONSHIP");}',
        "per-query decision diagnostics",
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
        '    groups[category].sort(function(a,b){\n      return order[a.relevanceTier]-order[b.relevanceTier] ||\n        b.relevanceScore-a.relevanceScore ||',
        '    groups[category].sort(function(a,b){\n'
        '      return eePrimaryRecommendationRank_(a,analysis.primaryArtists,[identity.artistId])-eePrimaryRecommendationRank_(b,analysis.primaryArtists,[identity.artistId]) ||\n'
        '        order[a.relevanceTier]-order[b.relevanceTier] ||\n'
        '        b.relevanceScore-a.relevanceScore ||',
        "primary artist result ordering",
    )
    code = replace_once(
        code,
        '  if(\n    (category==="LISTEN"||category==="WATCH") &&\n    /(^|\\.)music\\.apple\\.com$/.test(host)\n  ){\n    var musicUrl=raw.replace(\n      /^https?:\\/\\/[^\\/?#]+/i,\n      "https://geo.music.apple.com"\n    );',
        '  if(\n    (category==="LISTEN"||category==="WATCH") &&\n    /(^|\\.)music\\.apple\\.com$/.test(host)\n  ){\n    var musicUrl=raw.replace(\n      /^https?:\\/\\/[^\\/?#]+/i,\n      "https://geo.music.apple.com"\n    );\n\n'
        '    musicUrl=eeAppleAffiliateSetParam_(musicUrl,"at","1010lScn");\n'
        '    musicUrl=eeAppleAffiliateSetParam_(musicUrl,"app","music");\n'
        '    musicUrl=eeAppleAffiliateSetParam_(musicUrl,"ct","ee-related");\n'
        '    musicUrl=eeAppleAffiliateSetParam_(musicUrl,"ls","1");\n\n'
        '    return musicUrl;\n'
        '  }\n\n'
        '  if(category==="LISTEN"&&/(^|\\.)itunes\\.apple\\.com$/.test(host)){\n'
        '    var musicUrl=raw;',
        "Apple Music legacy-host attribution",
    )
    code = replace_once(
        code,
        '  if(category==="WATCH"&&/(^|\\.)tv\\.apple\\.com$/.test(host)){\n'
        '    var tvUrl=eeAppleAffiliateSetParam_(raw,"at","1010lScn");\n'
        '    tvUrl=eeAppleAffiliateSetParam_(tvUrl,"ct","ee-related");\n'
        '    return tvUrl;\n'
        '  }\n\n'
        '  return raw;',
        '  if(category==="WATCH"&&/(^|\\.)(?:tv\\.apple\\.com|itunes\\.apple\\.com)$/.test(host)){\n'
        '    var tvUrl=eeAppleAffiliateSetParam_(raw,"at","1010lScn");\n'
        '    tvUrl=eeAppleAffiliateSetParam_(tvUrl,"ct","ee-related");\n'
        '    return tvUrl;\n'
        '  }\n\n'
        '  if(category==="READ"&&/(^|\\.)(?:books\\.apple\\.com|itunes\\.apple\\.com)$/.test(host)){\n'
        '    return /(?:[?&])at=1010lScn(?:[&#]|$)/i.test(raw)?raw:"";\n'
        '  }\n\n'
        '  return raw;',
        "affiliate-safe TV and Books URLs",
    )
    code = replace_once(
        code,
        '  var priceValue=raw.collectionPrice!=null?raw.collectionPrice:(raw.trackPrice!=null?raw.trackPrice:raw.price);\n\n  return {',
        '  var affiliateUrl=eeAffiliateUrl_(query.category,url);if(!affiliateUrl)return null;\n'
        '  var priceValue=raw.collectionPrice!=null?raw.collectionPrice:(raw.trackPrice!=null?raw.trackPrice:raw.price);\n\n  return {',
        "reject unattributed Apple products",
    )
    code = replace_once(
        code,
        '    url:eeAffiliateUrl_(query.category,url),',
        '    url:affiliateUrl,',
        "use validated affiliate URL",
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
        '      var person=analysis.people[subjectIndex];if((query.category==="WATCH"||query.category==="READ")&&eeNorm_(person)!==primary)continue;\n'
        '      var credited=[].concat(raw.cast||[]).concat(raw.performers||[]).concat(raw.director||[]).some(function(name){return eeNorm_(name)===eeNorm_(person);});\n'
        '      if((query.category!=="WATCH"&&eeContains_(title,person))||(query.category==="WATCH"&&credited)){\n'
        '        score=92;tier="DIRECT";reason=query.category==="WATCH"?"Apple cast or credits identify the article subject.":"Apple title directly names the article subject.";\n'
        '      }',
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
    code = code.replace(
        "function eeSaveEntityProfile_(profile) {",
        "function eeSaveEntityProfile_(profile) {if(typeof EE_APPLE_READ_ONLY_GENERATION!==\"undefined\"&&EE_APPLE_READ_ONLY_GENERATION)return profile;"
    )
    code = code.replace(
        "function eeSaveIdentityMapping_(record) {",
        "function eeSaveIdentityMapping_(record) {if(typeof EE_APPLE_READ_ONLY_GENERATION!==\"undefined\"&&EE_APPLE_READ_ONLY_GENERATION)return record;"
    )
    code = replace_once(
        code,
        "function doGet(event) {",
        ARTIST_REGISTRY + "\n\nfunction doGet(event) {",
        "artist registry architecture",
    )
    code = replace_once(
        code,
        "function eeDiscoverArtistsWorker() {",
        PRODUCTION_ORCHESTRATOR + "\n\nfunction eeDiscoverArtistsMaintenanceWorker_() {",
        "live single-trigger production orchestration",
    )
    code = replace_once(
        code,
        "function eeRefreshStaleArtistsWorker() {",
        "function eeRefreshStaleArtistsMaintenanceWorker_() {",
        "internal stale enrichment worker",
    )
    code = replace_once(
        code,
        "function eeAssembleArticlePayloadsWorker() {",
        "function eeAssembleArticlePayloadsMaintenanceWorker_() {",
        "internal assembly worker",
    )
    code = replace_once(
        code,
        "function eeSeedArtistCataloguesFromGeneration2() {",
        LEGACY_MAINTENANCE_ENTRY_POINTS + "\n\nfunction eeSeedArtistCataloguesFromGeneration2() {",
        "idle legacy scheduled entry points",
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
