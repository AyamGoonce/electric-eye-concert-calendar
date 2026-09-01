var EE_APPLE_CONFIG = Object.freeze({
  enabled: true,
  blogId: "8469240496875020286",
  feedUrl: "https://www.electriceyerock.com/feeds/posts/default",
  storefront: "FR",
  searchLimit: 50,
  generationVersion: 3,
  artistIndexUrl: "https://archive.electriceyerock.com/proof/artist-index.json",
  minimumRequestIntervalMs: 10000,
  payloadCacheSeconds: 21600,
  backfillBatchSize: 1,
  spreadsheetProperty: "EE_APPLE_SPREADSHEET_ID"
});

function eeAppleSettings_() {
  var properties = PropertiesService.getScriptProperties();
  return {
    enabled: properties.getProperty("EE_APPLE_ENABLED") === "true" && EE_APPLE_CONFIG.enabled,
    spreadsheetId: properties.getProperty(EE_APPLE_CONFIG.spreadsheetProperty) || "",
    storefront: properties.getProperty("EE_APPLE_STOREFRONT") || EE_APPLE_CONFIG.storefront
  };
}

function eeApplePostAllowed_(postId) {
  var settings = eeAppleSettings_();
  return settings.enabled && /^[0-9]+$/.test(String(postId || ""));
}


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
  console.log(JSON.stringify({type:"APPLE_ARTIST_DISCOVERY",artistKey:diagnostic.artistKey,canonicalName:diagnostic.canonicalName,queries:diagnostic.queries,appleCalls:diagnostic.appleCalls,cacheHits:diagnostic.cacheHits,terminalStatus:String(status||""),terminalReason:String(reason||""),elapsedMs:Math.max(0,Date.now()-diagnostic.startedAt),stoppedBy:eeDiscoveryDiagnosticStopReason_(error)}));
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

function eeAppleTvHtmlDecode_(value) {
  return String(value||"")
    .replace(/&amp;/g,"&")
    .replace(/&quot;/g,'"')
    .replace(/&#39;|&apos;/g,"'")
    .replace(/&lt;/g,"<")
    .replace(/&gt;/g,">");
}

function eeAppleTvJsonDecode_(value) {
  try {
    return JSON.parse('"' + String(value||"") + '"');
  } catch(error) {
    return String(value||"")
      .replace(/\\\//g,"/")
      .replace(/\\"/g,'"')
      .replace(/\\\\/g,"\\");
  }
}

function eeAppleTvSubject_(term) {
  return String(term||"")
    .replace(/\s+(?:documentary|concert|live|film)\s*$/i,"")
    .trim();
}


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

function eeAppleTvItemsFromHtml_(html, storefront, term) {
  html=String(html||"");
  var subject=eeAppleTvSubject_(term);
  var items=[];
  var seen={};

  /*
   * First parse server-rendered search cards. Attribute order and the
   * distance between href and artwork are deliberately not assumed.
   */
  var cardPattern=/<a\b[^>]*data-testid=["']search-card-lockup["'][^>]*>[\s\S]*?<\/a>/gi;
  var card;

  while((card=cardPattern.exec(html))){
    var block=card[0];
    var opening=(block.match(/^<a\b[^>]*>/i)||[""])[0];

    var titleMatch=opening.match(/\baria-label=(["'])([\s\S]*?)\1/i);
    var hrefMatch=opening.match(/\bhref=(["'])([\s\S]*?)\1/i);

    if(!titleMatch||!hrefMatch)continue;

    var title=eeAppleTvHtmlDecode_(titleMatch[2]);
    var url=eeAppleTvHtmlDecode_(hrefMatch[2]);

    if(url.indexOf("/")===0)url="https://tv.apple.com"+url;
    if(!/^https:\/\/tv\.apple\.com\//i.test(url))continue;

    var idMatch=url.match(/\/(umc\.cmc\.[a-z0-9]+)(?:[/?#]|$)/i);
    if(!idMatch)continue;

    var srcsetMatch=block.match(/\bsrcset=(["'])([\s\S]*?)\1/i);
    var artwork="";

    if(srcsetMatch){
      artwork=eeAppleTvHtmlDecode_(srcsetMatch[2])
        .split(",")[0]
        .trim()
        .split(/\s+/)[0];
    }

    eeAppleTvPush_(items,seen,{
      id:idMatch[1],
      title:title,
      url:url,
      artworkUrl:artwork,
      mediaType:/\/show\//i.test(url)?"TV Show":"Film"
    },storefront,subject);
  }

  /*
   * Apple also keeps additional search results in embedded JSON. These
   * often are not rendered as <a> cards in the initial HTML, so the old
   * parser never saw them.
   */
  var marker='"$kind":"SearchCardComponent"';
  var offset=0;

  while(true){
    var start=html.indexOf(marker,offset);
    if(start<0)break;

    var next=html.indexOf(marker,start+marker.length);
    var end=next<0?Math.min(html.length,start+20000):Math.min(next,start+20000);
    var block=html.slice(start,end);

    var idMatch=block.match(/"id":"(umc\.cmc\.[a-z0-9]+)"/i);
    var titleMatch=block.match(/"title":"((?:\\.|[^"\\])*)"/);
    var typeMatch=block.match(/"type":"((?:\\.|[^"\\])*)"/);
    var artworkMatch=block.match(/"artwork":\{"template":"((?:\\.|[^"\\])*)"/);
    var descriptionMatch=block.match(/"description":"((?:\\.|[^"\\])*)"/);
    var castMatches=block.match(/"name":"((?:\\.|[^"\\])*)"/g)||[];

    if(idMatch&&titleMatch){
      var id=idMatch[1];
      var title=eeAppleTvJsonDecode_(titleMatch[1]);
      var mediaType=typeMatch?eeAppleTvJsonDecode_(typeMatch[1]):"Film";
      var artwork=artworkMatch?eeAppleTvJsonDecode_(artworkMatch[1]):"";

      if(artwork){
        artwork=artwork
          .replace(/\{w\}/g,"600")
          .replace(/\{h\}/g,"900")
          .replace(/\{f\}/g,"jpg");
      }

      var idPattern=id.replace(/[.*+?^${}()|[\]\\]/g,"\\$&");
      var urlPattern=new RegExp(
        "https:\\/\\/tv\\.apple\\.com\\/[^\"\\\\\\s]*"+idPattern,
        "i"
      );
      var urlMatch=block.match(urlPattern);

      if(!urlMatch){
        var globalStart=Math.max(0,start-3000);
        var globalEnd=Math.min(html.length,end+8000);
        urlMatch=html.slice(globalStart,globalEnd).match(urlPattern);
      }

      if(urlMatch){
        eeAppleTvPush_(items,seen,{
          id:id,
          title:title,
          url:eeAppleTvJsonDecode_(urlMatch[0]),
          artworkUrl:artwork,
          mediaType:/série|series|show/i.test(mediaType)?"TV Show":"Film",
          description:descriptionMatch?eeAppleTvJsonDecode_(descriptionMatch[1]):"",
          cast:castMatches.map(function(value){var match=value.match(/"name":"((?:\\.|[^"\\])*)"/);return match?eeAppleTvJsonDecode_(match[1]):"";}).filter(Boolean)
        },storefront,subject);
      }
    }

    offset=start+marker.length;
  }

  return items;
}

function eeAppleTvSearch_(term, storefront) {
  var url="https://tv.apple.com/"+String(storefront||"FR").toLowerCase()+"/search?term="+encodeURIComponent(term);
  var cache=CacheService.getScriptCache();
  var key="apple-tv:"+Utilities.base64EncodeWebSafe(
    Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256,url)
  ).slice(0,36);

  var cached=cache.get(key);
  if(cached)return JSON.parse(cached);

  var response=eeAppleFetch_(url,{muteHttpExceptions:true,headers:{"User-Agent":"Mozilla/5.0"}},"APPLE_TV_SEARCH");

  var items=eeAppleTvItemsFromHtml_(
    response.getContentText(),
    storefront,
    term
  );

  var text=JSON.stringify(items);
  if(text.length<95000)cache.put(key,text,21600);

  return items;
}

function eeFetchPosts_(startIndex, maxResults) {
  var url = EE_APPLE_CONFIG.feedUrl + "?alt=json&orderby=published&start-index=" + encodeURIComponent(startIndex) + "&max-results=" + encodeURIComponent(maxResults);
  var response = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
  if (response.getResponseCode() !== 200) throw new Error("Blogger feed returned " + response.getResponseCode());
  return ((JSON.parse(response.getContentText()).feed || {}).entry || []).map(function(entry){
    var alternate = (entry.link || []).filter(function(link){return link.rel === "alternate";})[0];
    return {id:String(entry.id.$t).split("post-").pop(),title:(entry.title||{}).$t||"",url:alternate?alternate.href:"",content:(entry.content||{}).$t||(entry.summary||{}).$t||"",labels:(entry.category||[]).map(function(category){return category.term;}),published:(entry.published||{}).$t||"",updated:(entry.updated||{}).$t||""};
  });
}


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


function eeProcessPost_(post, retryCount) {

  if (!eeAppleSettings_().enabled) {
    return {
      schemaVersion: 1,
      postId: String(post.id),
      categories: []
    };
  }

  try {

    var payload = eeGeneratePayload_(post);
    var hasRecommendations=eePayloadHasRecommendations_(payload);

    if (hasRecommendations) {
      eePutPayload_(post, payload, "READY", "", retryCount);
    } else {
      eePutPayload_(post, payload, "EMPTY", String((payload.diagnostics||{}).emptyClassification||"EMPTY_OTHER"), retryCount);
    }

    return payload;

  } catch(error) {

    try {
      eePutPayload_(
        post,
        {
          schemaVersion: 1,
          postId: String(post.id),
          categories: []
        },
        "ERROR",
        String(error && error.message || error),
        retryCount
      );
    } catch(storeError) {}

    throw error;

  }

}

function eeBackfillBatch(silent) {
  var settings = eeAppleSettings_();

  if (!settings.enabled) {
    var disabledResult = {status:"DISABLED"};
    console.log(JSON.stringify(disabledResult, null, 2));
    return disabledResult;
  }

  var properties = PropertiesService.getScriptProperties();
  var start = Math.max(1, Number(properties.getProperty("EE_APPLE_BACKFILL_INDEX") || 1));
  var posts = eeFetchPosts_(start, EE_APPLE_CONFIG.backfillBatchSize);

  if (!posts.length) {
    var completeResult = {
      status:"COMPLETE",
      processed:0,
      nextIndex:start,
      results:[]
    };

    if (!silent) console.log(JSON.stringify(completeResult, null, 2));
    return completeResult;
  }

  properties.setProperty("EE_APPLE_BACKFILL_COMPLETE", "false");
  var retryLater=null;
  var results = [];

  posts.forEach(function(post) {
    try {
      var existing = eeGetPayload_(post.id);

      if (eePayloadHasRecommendations_(existing)) {
        results.push({
          postId:String(post.id),
          title:post.title,
          status:"SKIPPED_READY"
        });
        return;
      }

      var payload = eeProcessPost_(post);
      var counts = {};

      (payload.categories || []).forEach(function(group) {
        counts[String(group.category || "")] =
          Array.isArray(group.items) ? group.items.length : 0;
      });

      var hasRecommendations = Object.keys(counts).some(function(category) {
  return counts[category] > 0;
});

results.push({
  postId:String(post.id),
  title:post.title,
  status:hasRecommendations ? "READY" : "EMPTY",
  categoryCounts:counts
});

    } catch(error) {
      if(error&&error.retryable)retryLater={postId:String(post.id),status:"RETRY_LATER",error:String(error.code||error.message||error)};
      else results.push({postId:String(post.id),title:post.title,status:"ERROR",error:String(error&&error.message||error)});
    }
  });

  if(retryLater)return {status:"RETRY_LATER",startIndex:start,fetched:posts.length,nextIndex:start,results:results.concat([retryLater])};
  var next = start + posts.length;
  properties.setProperty("EE_APPLE_BACKFILL_INDEX", String(next));

  var result = {
    status:"OK",
    startIndex:start,
    fetched:posts.length,
    nextIndex:next,
    results:results
  };

  if (!silent) console.log(JSON.stringify(result, null, 2));

  return result;
}

function eeProcessNewestPosts() {
  if (!eeAppleSettings_().enabled) return {status:"DISABLED"};

  var posts = eeFetchPosts_(1, 10);
  var results = [];

  posts.forEach(function(post) {
    try {
      var existingNewest = eeGetPayload_(post.id);

      if (eePayloadHasRecommendations_(existingNewest)) {
        results.push({postId:String(post.id),status:"SKIPPED_READY"});
        return;
      }

      var payload=eeProcessPost_(post);
      results.push({postId:String(post.id),status:eePayloadHasRecommendations_(payload)?"READY":"EMPTY",categories:(payload.categories||[]).map(function(group){return [group.category,group.items.length];})});
    } catch(error) {
      results.push({
        postId:String(post.id),
        status:"ERROR",
        error:String(error && error.message || error)
      });
    }
  });

  return {status:"OK",results:results};
}

function eeTitleRoleRelationship_(post) {
  var raw=String(post.title||"").trim();
  var title=raw
    .replace(/^\s*(?:album|record|concert|live)\s+review\s*:\s*/i,"")
    .replace(/^\s*(?:r\.?i\.?p\.?|interview)\s*:?\s*/i,"");

  var match=title.match(/^(.{1,80}?),\s*(?:drummer|guitarist|bassist|bass player|singer|vocalist|frontman|keyboardist|pianist|organist|multi-instrumentalist|saxophonist|trumpeter|violinist|producer|songwriter|member)\s+(?:of|for|with|in)\s+(.+?)\s*$/i);
  if(!match)return null;

  var person=String(match[1]||"").trim();
  var artist=String(match[2]||"").replace(/[.!?]+$/,"").trim();

  if(!person||!artist||eeNorm_(person)===eeNorm_(artist))return null;
  return {person:person,artist:artist,source:"title role relationship"};
}

function eeEntitySignalCandidates_(post) {
  var generic=/^(?:news|review|album review|record review|concert review|live review|interview|obituary|r\.?i\.?p\.?|music|rock|hard rock|classic rock|alternative rock|indie rock|blues|blues rock|metal|heavy metal|country|folk|americana|pop|punk|jazz|electronic|festival|tour|video|new|dates?|releases?|announces?|paris|album|single|song|track|show|tickets?|playlist|friday'?s playlist)$/i;
  var values=[],rawTitle=String(post.title||"").trim(),title=rawTitle.replace(/^\s*(?:album|record|concert|live)\s+review\s*:\s*/i,"").replace(/^\s*(?:r\.?i\.?p\.?|interview)\s*:?\s*/i,"");
  var titleLead=title.split(/\s+[–—]\s+/)[0].trim();
  var role=eeTitleRoleRelationship_(post);

  if(role){
    values.push({name:role.artist,strength:110,source:"title role primary artist"});
    values.push({name:role.person,strength:105,source:"title role article subject"});
  }

  var concertMatch=title.match(/^(.+?)\s+@\s+.+?(?:\s+-\s+.+)?$/);
  var concertSubject=concertMatch?String(concertMatch[1]||"").trim():"";

  var editorialMatch=title.match(/^(?:watch|hear|listen to|stream|see|check out|premiere)\s+(.{1,80}?)(?=[’'](?:s\b|\s)|\s+(?:performs?|performing|plays?|playing|covers?|covering|releases?|releasing|shares?|sharing|announces?|announcing|returns?|returning|debuts?|debuting|unveils?|unveiling|drops?|dropping|presents?|presenting)\b)/i);
  var editorialSubject=editorialMatch?String(editorialMatch[1]||"").replace(/[.!?:;,]+$/,"").trim():"";

  if(editorialSubject&&!generic.test(editorialSubject)&&eeNorm_(editorialSubject).split(" ").length<=7){
    values.push({name:editorialSubject,strength:102,source:"editorial action title subject"});
  }

  if(concertSubject){
    if(!generic.test(concertSubject)&&eeNorm_(concertSubject).split(" ").length<=7){
      values.push({name:concertSubject,strength:100,source:"concert title subject"});
    }
  }else{
    var separator=title.match(/\s+[–—-]\s+|\s*:\s+|\s*,\s*/);
    if(separator){
      var subject=title.slice(0,separator.index).trim();
      if(subject&&!generic.test(subject)&&eeNorm_(subject).split(" ").length<=7){
        values.push({name:subject,strength:100,source:"title structure"});
      }
    }
  }

  (post.labels||[]).forEach(function(label){
    var text=String(label||"").trim(),words=eeNorm_(text).split(" ");
    if(!text||generic.test(text)||words.length>7)return;

    if(concertSubject){
      if(eeNorm_(text)===eeNorm_(concertSubject)){
        values.push({name:text,strength:96,source:"concert-title-corroborated label"});
      }
    }else if(eeContains_(titleLead,text)){
      values.push({name:text,strength:96,source:"title-corroborated label"});
    }
  });

  var seen={};
  return values.filter(function(value){
    var key=eeNorm_(value.name);
    if(!key||seen[key])return false;
    seen[key]=true;
    return true;
  }).sort(function(a,b){
    return b.strength-a.strength||eeNorm_(a.name).localeCompare(eeNorm_(b.name));
  }).slice(0,4);
}

function eeAppleLabelFallbackArtists_(post) {
  var generic=/^(?:news|review|album review|record review|concert|concert review|live report|live review|interview|obituary|r\.?i\.?p\.?|music|rock|hard rock|classic rock|alternative rock|indie rock|progressive rock|prog|blues|blues rock|metal|heavy metal|country|folk|americana|pop|punk|jazz|electronic|festival|tour|video|new|dates?|releases?|announces?|paris|album|single|song|track|show|tickets?|photos?|playlist|friday'?s playlist)$/i;
  var body=eeNorm_(String(post.content||"").replace(/<[^>]+>/g," ").replace(/&nbsp;|&#160;/gi," "));
  var storefront=eeAppleSettings_().storefront;

  var candidates=(post.labels||[]).map(function(label){
    var name=String(label||"").trim();
    var normalized=eeNorm_(name);
    var words=normalized.split(" ").filter(Boolean);
    var mentions=normalized?body.split(normalized).length-1:0;
    return {name:name,normalized:normalized,words:words.length,mentions:mentions};
  }).filter(function(candidate){
    return candidate.name&&!generic.test(candidate.name)&&candidate.words>=2&&candidate.mentions>=2;
  }).sort(function(a,b){
    return b.mentions-a.mentions||a.normalized.localeCompare(b.normalized);
  }).slice(0,8);

  var validated=[];

  candidates.forEach(function(candidate){
    var response=eeAppleSearch_({
      term:candidate.name,
      storefront:storefront,
      media:"music",
      entity:"album"
    });

    var exact=(response.results||[]).filter(function(raw){
      return eeNorm_(raw.artistName||"")===candidate.normalized;
    });

    var uniqueAlbums={};
    exact.forEach(function(raw){
      var id=String(raw.collectionId||"");
      var title=eeNorm_(raw.collectionName||"");
      if(id||title)uniqueAlbums[id+"|"+title]=true;
    });

    if(Object.keys(uniqueAlbums).length>=3)validated.push(candidate.name);
  });

  return validated.length>=2?eeUnique_(validated):[];
}

function eePublicEntityJson_(url) {
  var key="ee-entity:"+Utilities.base64EncodeWebSafe(Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256,url)).slice(0,36);
  var cache=CacheService.getScriptCache();
  var cached=cache.get(key);
  if(cached)return JSON.parse(cached);

  var lock=LockService.getScriptLock();
  lock.waitLock(30000);

  try {
    cached=cache.get(key);
    if(cached)return JSON.parse(cached);

    var properties=PropertiesService.getScriptProperties();
    var retryable={429:true,500:true,502:true,503:true,504:true};
    var attempts=3;
    var lastError=null;

    for(var attempt=0;attempt<attempts;attempt+=1){
      var last=Number(properties.getProperty("EE_ENTITY_LAST_REQUEST_AT")||0);
      var wait=Math.max(0,1100-(Date.now()-last));
      if(wait)Utilities.sleep(wait);

      try {
        var response=UrlFetchApp.fetch(url,{
          muteHttpExceptions:true,
          headers:{
            Accept:"application/json",
            "User-Agent":"ElectricEyeRelatedApple/1.0 (https://www.electriceyerock.com/)"
          }
        });

        properties.setProperty("EE_ENTITY_LAST_REQUEST_AT",String(Date.now()));

        var code=response.getResponseCode();

        if(code===200){
          var value=JSON.parse(response.getContentText());
          var text=JSON.stringify(value);
          if(text.length<95000)cache.put(key,text,21600);
          return value;
        }

        lastError=new Error("MusicBrainz returned "+code);

        if(!retryable[code]){
          throw lastError;
        }

      } catch(error) {
        lastError=error;
      }

      if(attempt<attempts-1){
        Utilities.sleep(1500*Math.pow(2,attempt));
      }
    }

    throw lastError||new Error("MusicBrainz request failed");

  } finally {
    lock.releaseLock();
  }
}
function eeAppleStrongTitleProfile_(signal) {
  if(Number(signal.strength||0)<100)return null;

  var response=eeAppleSearch_({
    term:signal.name,
    storefront:eeAppleSettings_().storefront,
    media:"music",
    entity:"album"
  });

  var needle=eeNorm_(signal.name),byArtist={};

  (response.results||[]).forEach(function(raw){
    if(eeNorm_(raw.artistName||"")!==needle)return;

    var artistId=String(raw.artistId||"");
    if(!artistId)return;

    if(!byArtist[artistId]){
      byArtist[artistId]={
        artistId:artistId,
        name:String(raw.artistName||signal.name),
        albums:{}
      };
    }

    var albumKey=String(raw.collectionId||"")+"|"+eeNorm_(raw.collectionName||"");
    if(albumKey!=="|")byArtist[artistId].albums[albumKey]=true;
  });

  var candidates=Object.keys(byArtist).map(function(key){
    var candidate=byArtist[key];
    candidate.albumCount=Object.keys(candidate.albums).length;
    return candidate;
  }).filter(function(candidate){
    return candidate.albumCount>=3;
  });

  if(candidates.length!==1)return null;

  var chosen=candidates[0];

  return {
    name:chosen.name,
    aliases:eeUnique_([signal.name,chosen.name]),
    priority:Number(signal.strength||100),
    appleArtistId:chosen.artistId,
    confidence:"HIGH",
    evidence:[
      signal.source+" exact Apple catalogue match",
      String(chosen.albumCount)+" exact-name album results"
    ],
    primaryArtists:[chosen.name],
    people:[],
    members:[],
    collaborators:[],
    producers:[],
    sideProjects:[],
    relatedArtists:[]
  };
}

function eeMusicBrainzResolve_(signal) {
  var search=eePublicEntityJson_("https://musicbrainz.org/ws/2/artist/?query=artist:%22"+encodeURIComponent(signal.name)+"%22&limit=5&fmt=json"),needle=eeNorm_(signal.name),exact=(search.artists||[]).filter(function(artist){var names=[artist.name].concat((artist.aliases||[]).map(function(alias){return alias.name;}));return Number(artist.score||0)>=95&&names.some(function(name){return eeNorm_(name)===needle;});});
  if(exact.length!==1)return null;var artist=exact[0],detail=eePublicEntityJson_("https://musicbrainz.org/ws/2/artist/"+encodeURIComponent(artist.id)+"?inc=artist-rels&fmt=json"),profile={name:artist.name,aliases:eeUnique_([signal.name].concat((artist.aliases||[]).map(function(alias){return alias.name;}))),priority:Number(artist.score||0),musicBrainzId:artist.id,confidence:"HIGH",evidence:[signal.source+" exact match","MusicBrainz score "+String(artist.score)],primaryArtists:[artist.name],people:artist.type==="Person"?[artist.name]:[],members:[],collaborators:[],producers:[],sideProjects:[],relatedArtists:[]};
  (detail.relations||[]).forEach(function(relation){if(relation["target-type"]!=="artist"||!relation.artist||!relation.artist.name)return;var name=relation.artist.name,type=String(relation.type||"").toLowerCase();if(type==="member of band"){if(artist.type==="Group")profile.members.push(name);else profile.sideProjects.push(name);}else if(type==="collaboration"||type==="supporting musician")profile.collaborators.push(name);else if(type==="producer"||type==="producer position")profile.producers.push(name);else if(type==="subgroup"||type==="tribute")profile.relatedArtists.push(name);});
  ["members","collaborators","producers","sideProjects","relatedArtists"].forEach(function(key){profile[key]=eeUnique_(profile[key]).slice(0,12);});return profile;
}
function eeSaveEntityProfile_(profile) {
  var profiles=eeEntityProfiles_().filter(function(value){return String(value.musicBrainzId||"")!==String(profile.musicBrainzId||"")&&eeNorm_(value.name)!==eeNorm_(profile.name);});profiles.unshift(profile);profiles=profiles.slice(0,30);var properties=PropertiesService.getScriptProperties(),text=JSON.stringify(profiles);while(text.length>8500&&profiles.length>1){profiles.pop();text=JSON.stringify(profiles);}properties.setProperty("EE_APPLE_ENTITY_PROFILES",text);return profile;
}
function eeCachedEntityProfile_(post) {
  var signals=eeEntitySignalCandidates_(post),profiles=eeEntityProfiles_();for(var signalIndex=0;signalIndex<signals.length;signalIndex+=1){var needle=eeNorm_(signals[signalIndex].name),matched=profiles.filter(function(profile){return eeUnique_([profile.name].concat(profile.aliases||[])).some(function(alias){return eeNorm_(alias)===needle;});});if(matched.length===1)return matched[0];if(matched.length>1)return null;}return null;
}

function eeAcquireEntityProfile_(post) {
  var signals=eeEntitySignalCandidates_(post);
  var lastError=null;

  for(var index=0;index<signals.length;index+=1){
    var profile=null;

    try {
      profile=eeMusicBrainzResolve_(signals[index]);
      if(profile)return eeSaveEntityProfile_(profile);
    } catch(error) {
      lastError=error;
    }

    try {
      profile=eeAppleStrongTitleProfile_(signals[index]);
      if(profile)return profile;
    } catch(appleError) {
      if(!lastError)lastError=appleError;
    }
  }

  if(lastError)throw lastError;
  return null;
}

function eeIdentityMappings_() {
  try { return JSON.parse(PropertiesService.getScriptProperties().getProperty("EE_APPLE_IDENTITY_MAPPINGS") || "[]"); } catch(error) { return []; }
}
function eeSaveIdentityMapping_(record) {
  var records=eeIdentityMappings_().filter(function(value){return !(eeNorm_(value.alias)===eeNorm_(record.alias)&&String(value.artistId)===String(record.artistId));});
  records.push(record);PropertiesService.getScriptProperties().setProperty("EE_APPLE_IDENTITY_MAPPINGS",JSON.stringify(records));return record;
}
function eeResolveIdentity_(analysis, musicResults) {
  var subject=eeNorm_(analysis.primaryArtists[0]||""), existingId=String((analysis.existingAppleArtistIds||[])[0]||""), mappings=eeIdentityMappings_(), scores={};
  (musicResults||[]).forEach(function(raw){var id=String(raw.artistId||""),name=eeNorm_(raw.artistName),key=id;if(!id)return;if(!scores[key])scores[key]={artistId:id,score:0,releases:0,exactName:false};if(name===subject&&!scores[key].exactName){scores[key].exactName=true;scores[key].score+=30;}scores[key].releases+=1;});
  mappings.forEach(function(mapping){if(eeNorm_(mapping.alias)!==subject)return;if(mapping.status==="REJECTED")delete scores[String(mapping.artistId)];else if(scores[String(mapping.artistId)])scores[String(mapping.artistId)].score+=70;});

  if(existingId&&scores[existingId])scores[existingId].score+=70;
  var exactKeys=Object.keys(scores).filter(function(key){
    return scores[key].exactName;
  });

  var rankedExact=exactKeys.slice().sort(function(a,b){
    return scores[b].releases-scores[a].releases||
      String(a).localeCompare(String(b));
  });

  var dominantExactId=null;

  if(rankedExact.length>1){
    var topExactReleases=scores[rankedExact[0]].releases;
    var secondExactReleases=scores[rankedExact[1]].releases;

    if(
      topExactReleases>=6 &&
      topExactReleases>=secondExactReleases*2 &&
      topExactReleases-secondExactReleases>=4
    ){
      dominantExactId=rankedExact[0];
    }
  }

  Object.keys(scores).forEach(function(key){
    if(scores[key].releases<3)return;

    if(
      scores[key].exactName &&
      (exactKeys.length===1||key===dominantExactId)
    ){
      scores[key].score+=45;
    }else{
      scores[key].score+=18;
    }
  });
  var ranked=Object.keys(scores).map(function(key){return scores[key];}).sort(function(a,b){return b.score-a.score;});var best=ranked[0];
  if(!best||best.score<70||(ranked[1]&&best.score-ranked[1].score<15))return {level:best&&best.score>=45?"MODERATE":"LOW",artistId:null,confidenceScore:best?best.score:0};
  return {level:"HIGH",artistId:best.artistId,confidenceScore:best.score};
}

function eePayloadSheet_() {
  var settings = eeAppleSettings_();
  if (!settings.spreadsheetId) throw new Error("EE_APPLE_SPREADSHEET_ID is not configured");
  var spreadsheet = SpreadsheetApp.openById(settings.spreadsheetId);
  var sheet = spreadsheet.getSheetByName("Apple Payloads") || spreadsheet.insertSheet("Apple Payloads");
  if (sheet.getLastRow() === 0) sheet.appendRow(["postId", "canonicalUrl", "generatedAt", "storefront", "payloadJson", "status", "error", "retryCount"]);
  else if (sheet.getLastColumn() < 8) sheet.getRange(1, 8).setValue("retryCount");
  return sheet;
}

function eeEncodePayloadCell_(payload) {
  var json = JSON.stringify(payload);
  if (json.length <= 45000) return json;

  var gzip = Utilities.gzip(
    Utilities.newBlob(json, "application/json", "payload.json")
  );
  var encoded = "GZIP64:" + Utilities.base64Encode(gzip.getBytes());

  if (encoded.length > 49000) {
    throw new Error(
      "Encoded payload still exceeds safe Google Sheets cell size: " +
      encoded.length + " characters"
    );
  }

  return encoded;
}

function eeDecodePayloadCell_(value) {
  var stored = String(value || "");
  if (!stored) return null;

  if (stored.indexOf("GZIP64:") === 0) {
    var bytes = Utilities.base64Decode(stored.slice(7));
    var gzipBlob = Utilities.newBlob(bytes, "application/gzip", "payload.json.gz");
    var json = Utilities.ungzip(gzipBlob).getDataAsString("UTF-8");
    return JSON.parse(json);
  }

  return JSON.parse(stored);
}

function eeGetPayload_(postId) {
  var key = "ee-apple-payload:" + String(postId);
  var cached = CacheService.getScriptCache().get(key);
  if(cached){var cachedPayload=eeDecodePayloadCell_(cached);return eePayloadHasRecommendations_(cachedPayload)?cachedPayload:null;}

  var values = eePayloadSheet_().getDataRange().getValues();
  for (var row = 1; row < values.length; row += 1) {
    if (String(values[row][0]) === String(postId) && values[row][5] === "READY") {
      var stored = String(values[row][4] || "");
      if (!stored) return null;

      var payload=eeDecodePayloadCell_(stored);
      if(!eePayloadHasRecommendations_(payload))return null;
      CacheService.getScriptCache().put(key,stored,EE_APPLE_CONFIG.payloadCacheSeconds);
      return payload;
    }
  }
  return null;
}

function eePutPayload_(post, payload, status, error, retryCount) {
  var sheet = eePayloadSheet_();
  var values = sheet.getDataRange().getValues();
  var target = values.length + 1;

  for (var row = 1; row < values.length; row += 1) {
    if (String(values[row][0]) === String(post.id)) {
      target = row + 1;
      break;
    }
  }

  var storedPayload = eeEncodePayloadCell_(payload);

  sheet.getRange(target, 1, 1, 8).setValues([[
    String(post.id),
    post.url || "",
    new Date().toISOString(),
    payload.storefront || EE_APPLE_CONFIG.storefront,
    storedPayload,
    status,
    error || "",
    Math.max(0, Number(retryCount || 0))
  ]]);

  CacheService.getScriptCache().remove(
    "ee-apple-payload:" + String(post.id)
  );
}

function eeNorm_(value) { return String(value || "").toLowerCase().replace(/[’‘]/g, "'").replace(/[^a-z0-9'+]+/g, " ").replace(/\s+/g, " ").trim(); }
function eeContains_(value, term) { return (" " + eeNorm_(value) + " ").indexOf(" " + eeNorm_(term) + " ") !== -1; }
function eeUnique_(values) { var seen={};return (values||[]).map(function(value){return String(value||"").trim();}).filter(function(value){var key=eeNorm_(value);if(!key||seen[key])return false;seen[key]=true;return true;}); }
function eeEntityProfiles_() { try{return JSON.parse(PropertiesService.getScriptProperties().getProperty("EE_APPLE_ENTITY_PROFILES")||"[]");}catch(error){return [];} }
function eeEntityHints_(post) {
  var reviewed=eeReviewedPostSubjects_(post.id);
  if(reviewed.length)return {primaryArtists:reviewed,people:[],associatedPeople:[],collaborators:[],producers:[],sideProjects:[],relatedArtists:[],articleArtists:reviewed,existingAppleArtistIds:[]};
  var explicit = post.entityHints || post.entities || null;
  if (explicit) return explicit;

  var role = eeTitleRoleRelationship_(post);
  var signals = eeEntitySignalCandidates_(post);
  var selected = eeCachedEntityProfile_(post);
  var acquisitionError = null;

  if (!selected) {
    try {
      selected = eeAcquireEntityProfile_(post);
    } catch (error) {
      acquisitionError = error;
    }
  }

  var strongSignalArtists = signals
    .filter(function(signal) {
      return /title-corroborated label|concert-title-corroborated label|concert title subject|editorial action title subject/i.test(signal.source || "");
    })
    .map(function(signal) {
      return signal.name;
    });

  if (!selected) {
    var fallbackArtists = eeAppleLabelFallbackArtists_(post);
    var primaryArtists = eeUnique_(strongSignalArtists.concat(fallbackArtists || []));

    if (primaryArtists.length) {
      return {
        primaryArtists: primaryArtists,
        people: [],
        associatedPeople: [],
        collaborators: [],
        producers: [],
        sideProjects: [],
        relatedArtists: [],
        articleArtists: primaryArtists,
        existingAppleArtistIds: []
      };
    }

    if (acquisitionError) throw acquisitionError;
    return {};
  }

  var primary = role ? [role.artist] : [];
  var people = role ? [role.person] : [];
  var members = [];
  var collaborators = [];
  var producers = [];
  var sideProjects = [];
  var relatedArtists = [];

  primary = primary.concat(selected.primaryArtists || []);
  people = people.concat(selected.people || []);
  members = members.concat(selected.members || []);
  collaborators = collaborators.concat(selected.collaborators || []);
  producers = producers.concat(selected.producers || []);
  sideProjects = sideProjects.concat(selected.sideProjects || []);
  relatedArtists = relatedArtists.concat(selected.relatedArtists || []);

  var existingPrimaryNorms = {};
  eeUnique_(primary).forEach(function(name) {
    existingPrimaryNorms[eeNorm_(name)] = true;
  });

  strongSignalArtists.forEach(function(name) {
    var normalized = eeNorm_(name);
    if (!normalized) return;
    if (existingPrimaryNorms[normalized]) return;
    primary.push(name);
    existingPrimaryNorms[normalized] = true;
  });

  return {
    primaryArtists: eeUnique_(primary),
    people: eeUnique_(people),
    associatedPeople: eeUnique_(members),
    collaborators: eeUnique_(collaborators),
    producers: eeUnique_(producers),
    sideProjects: eeUnique_(sideProjects),
    relatedArtists: eeUnique_(relatedArtists),
    articleArtists: eeUnique_(strongSignalArtists),
    existingAppleArtistIds: eeUnique_(
      [selected.appleArtistId]
        .concat(selected.existingAppleArtistIds || [])
        .filter(Boolean)
    ).map(String)
  };
}

function eeBuildRelationshipGraph_(hints) {
  var nodes={},edges=[];
  function add(values,type,weight,relationship,source){eeUnique_(values).forEach(function(name){var key=eeNorm_(name),node={id:type+":"+key,name:name,normalizedName:key,type:type,weight:weight,relationship:relationship,source:source||null};if(!nodes[key]||nodes[key].weight<weight)nodes[key]=node;if(source)edges.push({from:eeNorm_(source),to:key,relationship:relationship,weight:weight});});}
  var subject=(hints.people||[])[0]||null,primary=(hints.primaryArtists||[])[0]||null;
  add(hints.people,"PERSON",100,"article subject",null);
  add(hints.primaryArtists,"ARTIST",96,"primary band or artist",subject);
  add(hints.associatedPeople||hints.members,"PERSON",90,"member of primary artist",primary);
  add(hints.articleArtists,"ARTIST",88,"artist explicitly identified in article",null);
  add(hints.sideProjects,"ARTIST",84,"side project",subject);
  add(hints.collaborators,"PERSON",80,"collaborator",primary);
  add(hints.producers,"PERSON",78,"producer or songwriter",primary);
  add(hints.relatedArtists,"ARTIST",76,"associated act",primary);
  return {nodes:Object.keys(nodes).map(function(key){return nodes[key];}).sort(function(a,b){return b.weight-a.weight||a.normalizedName.localeCompare(b.normalizedName);}),edges:edges};
}

function eeArticleAnalysis_(post) {

  var hints = eeEntityHints_(post),
      graph = eeBuildRelationshipGraph_(hints);

  var primaryArtists = eeUnique_(
    []
      .concat(hints.primaryArtists || [])
      .concat(hints.articleArtists || [])
  );

  return {
    postId: String(post.id),
    canonicalUrl: post.url || "",
    title: post.title || "",
    primaryArtists: primaryArtists,
    people: eeUnique_(hints.people || []),
    associatedPeople: eeUnique_(hints.associatedPeople || hints.members || []),
    existingAppleArtistIds: eeUnique_(hints.existingAppleArtistIds || []).map(String),
    relationshipGraph: graph
  };

}
function eeSearchPlan_(analysis, storefront) {
  if(!analysis.relationshipGraph.nodes.length)return [];
  var primary=eeNorm_(analysis.primaryArtists[0]||""),plan=[],seen={};
  function add(node,category,media,entity){var key=[category,media,entity,node.normalizedName,storefront].join("|");if(seen[key])return;seen[key]=true;plan.push({category:category,media:media,entity:entity,term:node.name,intent:node.type,relationship:node.relationship,relationshipWeight:node.weight,storefront:storefront});}
  analysis.relationshipGraph.nodes.filter(function(node){return node.weight>=76;}).forEach(function(node){add(node,"LISTEN","music","album");add(node,"WATCH","music","musicVideo");add(node,"READ","ebook","ebook");add(node,"READ","audiobook","audiobook");});
  return plan;
}

function eeRelationshipReason_(query, musicConfirmed) {
  var term=String(query.term||"").trim();
  var relationship=String(query.relationship||"").toLowerCase();
  var reason;

  if(relationship==="article subject"){
    reason=term+" is directly featured in the article.";
  }else if(relationship==="primary band or artist"){
    reason=term+" is the primary band or artist discussed in the article.";
  }else if(relationship==="member of primary artist"){
    reason=term+" is a member of the primary artist discussed in the article.";
  }else if(relationship==="artist explicitly identified in article"){
    reason=term+" is explicitly identified as a musical artist in the article.";
  }else if(relationship==="side project"){
    reason=term+" is a side project connected to the article subject.";
  }else if(relationship==="collaborator"){
    reason=term+" is a collaborator connected to the primary artist.";
  }else if(relationship==="producer or songwriter"){
    reason=term+" is a producer or songwriter connected to the primary artist.";
  }else if(relationship==="associated act"){
    reason=term+" is an associated act connected to the primary artist.";
  }else{
    reason=term+" has a verified musical relationship to the article subject.";
  }

  if(musicConfirmed)reason+=" Apple metadata confirms the musical identity.";
  return reason;
}

function eeCandidate_(raw, query, analysis) {
  var id=raw.collectionId||raw.trackId||raw.artistId;
  var title=raw.collectionName||raw.trackName||raw.artistName||"";
  var creator=raw.artistName||raw.sellerName||"";
  var fullDescription=String(raw.description||"").replace(/<[^>]+>/g," ").replace(/\s+/g," ").trim();
  var description=fullDescription.slice(0,800);
  var url=raw.collectionViewUrl||raw.trackViewUrl||raw.artistViewUrl||"";
  var combined=[title,creator,fullDescription].join(" ");
  var genres=(raw.genres||[raw.primaryGenreName||""]).join(" ");
  var primary=eeNorm_(analysis.primaryArtists[0]||"");
  var exactPrimaryCreator=eeNorm_(creator)===primary;
  var relationshipMatch=query.relationshipWeight&&(
    query.category==="LISTEN"
      ? eeNorm_(creator)===eeNorm_(query.term)
      : query.category==="READ"
        ? (eeNorm_(creator)===eeNorm_(query.term)||(query.intent==="PERSON"&&eeContains_(title,query.term)))
        : query.category==="WATCH"&&query.entity==="musicVideo"
          ? eeNorm_(creator)===eeNorm_(query.term)
          : ([].concat(raw.cast||[]).concat(raw.performers||[]).concat(raw.director||[]).some(function(name){return eeNorm_(name)===eeNorm_(query.term);})||(/documentary|documentaire|concert film|live concert|portrait|biograph/.test(eeNorm_(fullDescription))&&eeContains_(fullDescription,query.term)))
  );
  var score=0,tier="",reason="",readFallback=false;

  if(query.category==="READ"){
    var earlyReadTitle=eeNorm_(title);
    var earlyPrimaryPattern=primary?primary.replace(/[.*+?^${}()|[\]\\]/g,"\\$&"):"";
    if(/my dead dad|types of jokes|humor techniques/.test(earlyReadTitle))return null;
    if(earlyPrimaryPattern&&new RegExp("\\bv\\s+"+earlyPrimaryPattern+"\\b").test(earlyReadTitle))return null;
  }

  if(query.category==="LISTEN"&&exactPrimaryCreator){
    score=/greatest|compilation|karaoke|tribute/i.test(title)?93:96;
    tier="DIRECT";
    reason="Official release by the primary artist in the configured storefront.";
  } else if(query.category==="WATCH"&&query.entity==="musicVideo"&&exactPrimaryCreator){
    score=88;
    tier="CLOSELY_RELATED";
    reason="Official Apple Music video by the primary artist in the configured storefront.";
  } else {
    for(var subjectIndex=0;subjectIndex<analysis.people.length&&!score;subjectIndex+=1){
      var person=analysis.people[subjectIndex],credited=[].concat(raw.cast||[]).concat(raw.performers||[]).concat(raw.director||[]).some(function(name){return eeNorm_(name)===eeNorm_(person);});
      if((query.category!=="WATCH"&&eeContains_(title,person))||(query.category==="WATCH"&&credited)){
        score=92;tier="DIRECT";reason=query.category==="WATCH"?"Apple cast or credits identify the article subject.":"Apple title directly names the article subject.";
      }
    }

    if(!score&&query.category==="READ"&&relationshipMatch){
      var normalizedGenres=eeNorm_(genres);
      var relationshipMetadata=eeNorm_([title,fullDescription].join(" "));
      var musicGenre=/\bmusic\b|\bmusique\b/.test(normalizedGenres);
      var musicianSpecific=/\bmusician\b|\bguitarist\b|\bdrummer\b|\bbassist\b|\bcomposer\b|\bsongwriter\b|\bsinger\b|\bvocalist\b|\bmusic theory\b|\brecording artist\b|\bdiscograph\b|\balbum\b|\bconcert\b/.test(relationshipMetadata);

      if(musicGenre||musicianSpecific){
        score=Math.min(89,Number(query.relationshipWeight));
        tier=score>=84?"CLOSELY_RELATED":"CONTEXTUAL";
        reason=eeRelationshipReason_(query,true);
      }
    } else if(!score&&relationshipMatch){
      score=Math.min(89,Number(query.relationshipWeight));
      tier=score>=84?"CLOSELY_RELATED":"CONTEXTUAL";
      reason=eeRelationshipReason_(query,false);
    }
  }

  if(!score&&query.category==="READ"&&primary&&eeContains_(combined,primary)){
    var normalizedTitle=eeNorm_(title);
    var normalizedDescription=eeNorm_(fullDescription);
    var normalizedGenres2=eeNorm_(genres);
    var mentions=normalizedDescription.split(primary).length-1;
    var primaryPattern=primary.replace(/[.*+?^${}()|[\]\\]/g,"\\$&");
    var disallowed=new RegExp("\\bv\\s+"+primaryPattern+"\\b").test(normalizedTitle)||/my dead dad|types of jokes|humor techniques/.test(normalizedTitle);
    var broadSurvey=new RegExp("\\bfrom\\b.+\\bto "+primaryPattern+"\\b").test(normalizedTitle);
    var primaryInTitle=eeContains_(title,primary);
    var musicGenre2=/\bmusic\b|\bmusique\b/.test(normalizedGenres2);
    var readMusicMetadata=/\bmusician\b|\bguitarist\b|\bdrummer\b|\bbassist\b|\bcomposer\b|\bsongwriter\b|\bsinger\b|\bvocalist\b|\brecording artist\b|\bdiscograph\b|\balbum\b|\bconcert\b|\brock band\b|\bmetal band\b|\bmusical artist\b/.test(normalizedDescription);
    var titleMusicMatch=primaryInTitle&&!broadSurvey&&(musicGenre2||(mentions>=1&&readMusicMetadata));

    if(disallowed)return null;

    if(exactPrimaryCreator||titleMusicMatch){
      score=94;
      tier="DIRECT";
      reason=exactPrimaryCreator?"Apple Books item is by the primary artist.":"Apple title and music-specific metadata directly concern the primary artist.";
    } else if(mentions>=2&&musicGenre2){
      score=68;
      tier="CONTEXTUAL";
      readFallback=true;
      reason="A music-specific Apple Books item substantially features the primary artist.";
    } else if(broadSurvey&&musicGenre2){
      score=62;
      tier="CONTEXTUAL";
      readFallback=true;
      reason="A broader music study explicitly includes the primary artist.";
    } else {
      return null;
    }

  } else if(!score&&query.category==="WATCH"&&primary&&eeContains_(combined,primary)){
    var watchCredits=[].concat(raw.cast||[]).concat(raw.performers||[]).concat(raw.director||[]);
    var credited=watchCredits.some(function(name){return eeNorm_(name)===primary;});
    var described=eeNorm_(fullDescription).split(primary).length>2&&/documentary|documentaire|concert film|live concert|portrait|biograph/.test(eeNorm_(fullDescription));
    if(!credited&&!described)return null;
    score=credited?97:96;tier="DIRECT";reason=credited?"Apple cast or credits identify the primary artist.":"Apple metadata describes substantial long-form content about the primary artist.";
  }

  var minimum={LISTEN:82,WATCH:78,READ:60}[query.category];
  if(!id||!title||!url||score<minimum||(query.category==="LISTEN"&&/\s-\sSingle$/i.test(title)))return null;

  var priceValue=raw.collectionPrice!=null?raw.collectionPrice:(raw.trackPrice!=null?raw.trackPrice:raw.price);

  return {
    stableId:String(id),
    appleArtistId:String(raw.artistId||raw.collectionArtistId||"")||null,
    category:query.category,
    title:title,
    creator:creator,
    mediaType:raw.kind||raw.collectionType||raw.wrapperType||query.entity,
    artworkUrl:String(raw.artworkUrl512||raw.artworkUrl100||raw.artworkUrl60||"").replace("/100x100bb.","/600x600bb."),
    canonicalAppleUrl:url,
    url:eeAffiliateUrl_(query.category,url),
    storefront:query.storefront,
    price:(typeof priceValue==="number"&&priceValue>=0)?{value:priceValue,currency:raw.currency||null,formatted:raw.formattedPrice||null}:null,
    relevanceTier:tier,
    relevanceScore:score,
    relevanceReason:reason,
    relationshipContext:reason,
    readFallback:readFallback,
    releaseDate:raw.releaseDate||null,
    publisher:raw.publisher||null,
    narrator:raw.narrator||null,
    director:raw.director||null,
    cast:raw.cast||null,
    description:description||null
  };
}


function eeAppleAffiliateSetParam_(value,key,paramValue){
  var url=String(value||"");
  var hash="";
  var hashAt=url.indexOf("#");

  if(hashAt!==-1){
    hash=url.slice(hashAt);
    url=url.slice(0,hashAt);
  }

  var escapedKey=String(key).replace(/[.*+?^${}()|[\]\\]/g,"\\$&");
  var pattern=new RegExp("([?&])"+escapedKey+"=[^&#]*","i");
  var replacement="$1"+key+"="+encodeURIComponent(String(paramValue));

  if(pattern.test(url)){
    url=url.replace(pattern,replacement);
  } else {
    url+=(url.indexOf("?")===-1?"?":"&")+key+"="+encodeURIComponent(String(paramValue));
  }

  return url+hash;
}

function eeAffiliateUrl_(category,value){
  var raw=String(value||"");
  if(!raw)return raw;

  var hostMatch=raw.match(/^https?:\/\/([^\/?#]+)/i);
  if(!hostMatch)return raw;

  var host=String(hostMatch[1]||"").toLowerCase();

  if(
    (category==="LISTEN"||category==="WATCH") &&
    /(^|\.)music\.apple\.com$/.test(host)
  ){
    var musicUrl=raw.replace(
      /^https?:\/\/[^\/?#]+/i,
      "https://geo.music.apple.com"
    );

    musicUrl=eeAppleAffiliateSetParam_(musicUrl,"at","1010lScn");
    musicUrl=eeAppleAffiliateSetParam_(musicUrl,"app","music");
    musicUrl=eeAppleAffiliateSetParam_(musicUrl,"ct","ee-related");
    musicUrl=eeAppleAffiliateSetParam_(musicUrl,"ls","1");

    return musicUrl;
  }

  if(category==="WATCH"&&/(^|\.)tv\.apple\.com$/.test(host)){
    var tvUrl=eeAppleAffiliateSetParam_(raw,"at","1010lScn");
    tvUrl=eeAppleAffiliateSetParam_(tvUrl,"ct","ee-related");
    return tvUrl;
  }

  return raw;
}

function eeApplyReadFallbackPolicy_(items){
  var stronger=items.filter(function(item){return !item.readFallback;});
  return stronger.length>=8?stronger:items;
}

function eePrimaryExactArtistIds_(analysis,rows){
  var primary=eeNorm_(analysis.primaryArtists[0]||"");
  var ids=(analysis.existingAppleArtistIds||[]).map(String);

  (rows||[]).forEach(function(raw){
    if(eeNorm_(raw.artistName||"")!==primary)return;
    var id=raw.artistId||raw.collectionArtistId;
    if(id)ids.push(String(id));
  });

  return eeUnique_(ids).slice(0,8);
}

function eeAddCandidateToMap_(map,raw,query,analysis){
  var item=eeCandidate_(raw,query,analysis);
  if(!item)return false;

  var key=(item.category==="LISTEN"||item.category==="WATCH")
    ? item.category+":"+eeNorm_(item.creator)+"|"+eeNorm_(item.title)
    : item.category+":"+item.stableId;

  if(!map[key]||item.relevanceScore>map[key].relevanceScore){map[key]=item;}
  return true;
}

function eePrimaryLookupQuery_(analysis,storefront,category,entity){
  return {
    category:category,
    media:"music",
    entity:entity,
    term:analysis.primaryArtists[0]||"",
    intent:"PRIMARY_ARTIST",
    relationship:"primary band or artist",
    relationshipWeight:100,
    storefront:storefront
  };
}

function eeGeneratePayloadLegacy_(post) {
  var analysis=eeArticleAnalysis_(post);
  var settings=eeAppleSettings_();
  var plan=eeSearchPlan_(analysis,settings.storefront);
  if ((analysis.primaryArtists || []).length > 1) {
  var primarySet = {};
  analysis.primaryArtists.forEach(function(name) {
    primarySet[eeNorm_(name)] = true;
  });

  plan = plan.filter(function(query) {
    return query.intent === "ARTIST" &&
           primarySet[eeNorm_(query.term || "")];
  });
}
  var map={},musicResults=[];
  var diagnostics={primaryArtists:analysis.primaryArtists.slice(),identity:null,searchIntents:plan.map(function(query){return query.category+":"+query.entity+":"+query.term;}),rawResultCount:0,acceptedCount:0,rejectedCount:0,relationshipRejectedCount:0,rejectionReasons:{}};

  plan.forEach(function(query){
    var queryDiagnostic=eeDiscoveryDiagnosticQuery_(query);
    var response=eeAppleSearch_(query);
    eeDiscoveryDiagnosticCandidates_(queryDiagnostic,response);

    if(query.category==="LISTEN"){
      musicResults=musicResults.concat(response.results||[]);
    }

    diagnostics.rawResultCount+=(response.results||[]).length;
    (response.results||[]).forEach(function(raw){
      if(eeAddCandidateToMap_(map,raw,query,analysis)){diagnostics.acceptedCount+=1;eeDiscoveryDiagnosticDecision_(queryDiagnostic,true,"QUALIFYING_RELATIONSHIP");}
      else{diagnostics.rejectedCount+=1;diagnostics.relationshipRejectedCount+=1;diagnostics.rejectionReasons.NO_QUALIFYING_RELATIONSHIP=(diagnostics.rejectionReasons.NO_QUALIFYING_RELATIONSHIP||0)+1;eeDiscoveryDiagnosticDecision_(queryDiagnostic,false,"NO_QUALIFYING_RELATIONSHIP");}
    });
  });

  var exactPrimaryIds=eePrimaryExactArtistIds_(analysis,musicResults);
  var expandedAlbums=[];

  if(exactPrimaryIds.length){
    try{
      var expandedResponse=eeAppleLookup_({
        ids:exactPrimaryIds,
        entity:"album",
        storefront:settings.storefront
      });

      expandedAlbums=(expandedResponse.results||[]).filter(function(raw){
        return raw.collectionId &&
          eeNorm_(raw.artistName||"")===eeNorm_(analysis.primaryArtists[0]||"");
      });

      musicResults=musicResults.concat(expandedAlbums);
    }catch(error){if(error&&error.retryable)throw error;expandedAlbums=[];}
  }

  var identity=eeResolveIdentity_(analysis,musicResults);
  diagnostics.identity=identity;

  if(identity.level==="HIGH"){
    Object.keys(map).forEach(function(key){
      var item=map[key];

      if(
        item.relevanceTier==="DIRECT" &&
        (item.category==="LISTEN"||item.category==="WATCH") &&
        item.appleArtistId &&
        String(item.appleArtistId)!==String(identity.artistId) &&
        eeNorm_(item.creator||"")===eeNorm_(analysis.primaryArtists[0]||"")
      ){
        delete map[key];
      }
    });

    var directAlbumRows=expandedAlbums.filter(function(raw){
      return String(raw.artistId||raw.collectionArtistId||"")===
        String(identity.artistId);
    });

    if(!directAlbumRows.length&&identity.artistId){
      try{
        var directAlbumResponse=eeAppleLookup_({
          ids:[identity.artistId],
          entity:"album",
          storefront:settings.storefront
        });

        directAlbumRows=(directAlbumResponse.results||[]).filter(function(raw){
          return raw.collectionId &&
            String(raw.artistId||raw.collectionArtistId||"")===
              String(identity.artistId);
        });
      }catch(error){if(error&&error.retryable)throw error;directAlbumRows=[];}
    }

    var albumQuery=eePrimaryLookupQuery_(
      analysis,
      settings.storefront,
      "LISTEN",
      "album"
    );

    directAlbumRows.forEach(function(raw){
      eeAddCandidateToMap_(map,raw,albumQuery,analysis);
    });

    if(identity.artistId){
      try{
        var videoResponse=eeAppleLookup_({
          ids:[identity.artistId],
          entity:"musicVideo",
          storefront:settings.storefront
        });

        var videoQuery=eePrimaryLookupQuery_(
          analysis,
          settings.storefront,
          "WATCH",
          "musicVideo"
        );

        (videoResponse.results||[]).forEach(function(raw){
          if(!raw.trackId)return;
          if(String(raw.kind||"").toLowerCase()!=="music-video")return;
          if(
            String(raw.artistId||raw.collectionArtistId||"")!==
            String(identity.artistId)
          )return;
          eeAddCandidateToMap_(map,raw,videoQuery,analysis);
        });
      }catch(error){if(error&&error.retryable)throw error;}
    }
    try{
      eeAppleTvSearch_(analysis.primaryArtists[0]||"",settings.storefront).forEach(function(item){
        var key="WATCH:tv:"+String(item.stableId);
        if(!map[key]||item.relevanceScore>map[key].relevanceScore)map[key]=item;
      });
    }catch(error){if(error&&error.retryable)throw error;}
  }else{
    Object.keys(map).forEach(function(key){
      if(map[key].relevanceTier==="DIRECT"){
        delete map[key];
      }
    });
  }

  var order={DIRECT:0,CLOSELY_RELATED:1,CONTEXTUAL:2};
  var groups={LISTEN:[],WATCH:[],READ:[]};

  Object.keys(map).forEach(function(key){
    groups[map[key].category].push(map[key]);
  });

  var categories=[];

  ["LISTEN","WATCH","READ"].forEach(function(category){
    if(category==="READ"){
      groups[category]=eeApplyReadFallbackPolicy_(groups[category]);
    }

    groups[category].sort(function(a,b){
      return order[a.relevanceTier]-order[b.relevanceTier] ||
        b.relevanceScore-a.relevanceScore ||
        a.title.localeCompare(b.title) ||
        String(a.stableId).localeCompare(String(b.stableId));
    });

    if(groups[category].length){
      categories.push({category:category,items:groups[category]});
    }
  });

  diagnostics.finalCategoryCounts={};
  categories.forEach(function(group){diagnostics.finalCategoryCounts[group.category]=group.items.length;});
  diagnostics.emptyClassification=categories.length?null:eeEmptyClassification_(diagnostics);
  return {
    schemaVersion:1,
    generationVersion:EE_APPLE_CONFIG.generationVersion,
    generatedAt:new Date().toISOString(),
    postId:String(post.id),
    canonicalUrl:post.url||"",
    storefront:settings.storefront,
    subject:{
      title:post.title||"",
      primaryArtists:analysis.primaryArtists,
      people:analysis.people
    },
    identity:identity,
    categories:categories,
    diagnostics:diagnostics
  };
}


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
var EE_APPLE_ARTIST_TRANSIENT_RETRY_LIMIT=3;
var EE_APPLE_ARTIST_DEFERRED_RETRY_MS=6*60*60*1000;

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
  eeUpsertRow_(sheet,0,record.artistKey,[record.artistKey,record.canonicalName,1,1,record.appleArtistId||"",record.musicBrainzId||"",record.identityConfidence||"",record.status||"UNRESOLVED",eeEncodePayloadCell_(catalogue),generated,stale,record.representativePostId||"",record.error||"",Math.max(0,Number(record.transientRetryCount||0)),record.lastTransientError||"",record.retryAfter||""]);
}

function eeAssemblePayloadFromCatalogues_(post,analysis,catalogues) {
  var groups={LISTEN:{},WATCH:{},READ:{}},articleText=String(post.title||"")+" "+String(post.content||"").replace(/<[^>]+>/g," ");
  catalogues.forEach(function(record){((record.catalogue||{}).categories||[]).forEach(function(group){(group.items||[]).forEach(function(item){var ranked=JSON.parse(JSON.stringify(item)),boost=0;if(ranked.title&&eeExactEntityInText_(articleText,ranked.title))boost+=6;if(analysis.articleType==="interview"&&ranked.creator&&eeExactEntityInText_(post.title||"",ranked.creator))boost+=3;ranked.relevanceScore=Number(ranked.relevanceScore||0)+boost;var key=String(ranked.stableId||ranked.url||ranked.title),existing=groups[group.category]&&groups[group.category][key];if(groups[group.category]&&(!existing||Number(ranked.relevanceScore||0)>Number(existing.relevanceScore||0)))groups[group.category][key]=ranked;});});});
  var categories=[];["LISTEN","WATCH","READ"].forEach(function(category){var items=Object.keys(groups[category]).map(function(key){return groups[category][key];});items.sort(function(a,b){return Number(b.relevanceScore||0)-Number(a.relevanceScore||0)||String(a.title).localeCompare(String(b.title));});if(items.length)categories.push({category:category,items:items});});
  return {schemaVersion:1,generationVersion:EE_APPLE_CONFIG.generationVersion,generatedAt:new Date().toISOString(),postId:String(post.id),canonicalUrl:post.url||"",storefront:eeAppleSettings_().storefront,subject:{title:post.title||"",primaryArtists:analysis.primaryArtists,people:analysis.people||[]},identity:{level:analysis.identityConfidence,artistId:catalogues.length===1?catalogues[0].appleArtistId||null:null,confidenceScore:analysis.identityConfidence==="HIGH"?100:75},categories:categories,diagnostics:{architecture:"ARTIST_REGISTRY_V1",artistKeys:analysis.primaryArtistKeys,cacheHits:catalogues.length,emptyClassification:categories.length?null:(analysis.primaryArtistKeys.length?"EMPTY_NO_QUALIFYING_RELATIONSHIP":"EMPTY_NO_SUBJECT")}};
}

function eeDiscoverArtistCatalogue_(artist,post,forceRefresh) {
  var diagnostic=eeDiscoveryDiagnosticStart_(artist);
  var lease="CATALOGUE_"+String(artist.slug||"").replace(/[^A-Za-z0-9_-]/g,"_");
  if(!eeAcquireWorkerLease_(lease,360000)){var busy=new Error("ARTIST_DISCOVERY_BUSY");busy.code="ARTIST_DISCOVERY_BUSY";busy.retryable=true;eeDiscoveryDiagnosticFinish_(diagnostic,"RETRY_LATER",busy.code,busy);throw busy;}
  try{
    var existing=eeGetArtistCatalogue_(artist.slug);if(existing&&existing.status!=="UNRESOLVED"&&!forceRefresh){eeDiscoveryDiagnosticFinish_(diagnostic,existing.status,"EXISTING_CATALOGUE",null);return existing;}
    var legacy=eeGeneratePayloadLegacy_(post),identity=legacy.identity||{};
    var categories=(legacy.categories||[]).map(function(group){return {category:group.category,items:(group.items||[]).filter(function(item){return !item.creator||eeNorm_(item.creator)===eeNorm_(artist.canonicalName)||group.category!=="LISTEN";})};}).filter(function(group){return group.items.length;});
    var confidence=String(identity.level||"LOW"),appleArtistId=identity.artistId||artist.appleArtistId||"",status=(appleArtistId||confidence==="HIGH")?"RESOLVED":confidence==="MODERATE"?"AMBIGUOUS":"ERROR",errorReason=status==="ERROR"?"APPLE_ARTIST_DISCOVERY_EXHAUSTED":"";
    if(status==="ERROR")categories=[];
    var record={artistKey:artist.slug,canonicalName:artist.canonicalName,appleArtistId:appleArtistId,musicBrainzId:artist.musicBrainzId||"",identityConfidence:confidence,status:status,error:errorReason,categories:categories,representativePostId:String(post.id)};
    eePutArtistCatalogue_(record);var properties=PropertiesService.getScriptProperties();properties.setProperty("EE_APPLE_CATALOGUE_GENERATION_COUNT",String(Number(properties.getProperty("EE_APPLE_CATALOGUE_GENERATION_COUNT")||0)+1));record.catalogue={schemaVersion:1,generationVersion:EE_APPLE_CONFIG.generationVersion,artistKey:record.artistKey,canonicalName:record.canonicalName,categories:record.categories};eeDiscoveryDiagnosticFinish_(diagnostic,status,errorReason||(status==="RESOLVED"?"CONFIDENT_MATCH":"PLAUSIBLE_MATCH"),null);return record;
  }catch(error){eeDiscoveryDiagnosticFinish_(diagnostic,error&&error.retryable?"RETRY_LATER":"ERROR",String((error&&error.code)||(error&&error.message)||"DISCOVERY_ERROR"),error);throw error;
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
          var transientError=String(error.code||error.message||error),retryCount=Math.max(0,Number(values[row][13]||0))+1,retryAfter="";
          if(retryCount<EE_APPLE_ARTIST_TRANSIENT_RETRY_LIMIT){
            eePutArtistCatalogue_({artistKey:artistKey,canonicalName:canonicalName,identityConfidence:"UNRESOLVED",status:"UNRESOLVED",representativePostId:representativePostId,error:transientError,categories:[],transientRetryCount:retryCount,lastTransientError:transientError});
            properties.setProperty("EE_APPLE_ARTIST_DISCOVERY_INDEX",String(row));
            console.log(JSON.stringify({artistKey:artistKey,canonicalName:canonicalName,transientError:transientError,retryCount:retryCount,retryLimit:EE_APPLE_ARTIST_TRANSIENT_RETRY_LIMIT,cursor:row}));
            return {status:"RETRY_LATER",artistKey:artistKey,error:transientError,retryCount:retryCount,retryLimit:EE_APPLE_ARTIST_TRANSIENT_RETRY_LIMIT};
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
  try{var sheet=eeArtistCatalogueSheet_(),values=sheet.getDataRange().getValues(),properties=PropertiesService.getScriptProperties(),cursor=Math.max(1,Number(properties.getProperty("EE_APPLE_STALE_REFRESH_INDEX")||1));eeSetExecutionDeadline_(Date.now()+180000);
  for(var row=cursor;row<values.length;row+=1){
    var status=String(values[row][7]||""),isDeferred=status==="DEFERRED",isStale=status==="RESOLVED"&&values[row][10]&&Date.parse(String(values[row][10]))<=Date.now(),retryAfter=String(values[row][15]||"");
    if(!isStale&&(!isDeferred||!retryAfter||Date.parse(retryAfter)>Date.now())){properties.setProperty("EE_APPLE_STALE_REFRESH_INDEX",String(row+1));continue;}
    var artistKey=String(values[row][0]),canonicalName=String(values[row][1]),representativePostId=String(values[row][11]||""),registry=eeArtistRegistry_(),artist=registry.artists.filter(function(value){return value.slug===artistKey;})[0]||{slug:artistKey,canonicalName:canonicalName,aliases:[],ambiguityClass:"provisional"};
    try{
      var post=eeFetchPostById_(representativePostId),catalogue=eeDiscoverArtistCatalogue_(artist,post,true);
      properties.setProperty("EE_APPLE_STALE_REFRESH_INDEX",String(row+1));
      return {status:isDeferred?"DEFERRED_RETRIED":"REFRESHED",artistKey:artist.slug,terminalStatus:String(catalogue&&catalogue.status||""),cursor:row+1};
    }catch(error){
      var errorReason=String(error&&error.code||error&&error.message||error);
      if(error&&error.retryable){
        var retryCount=Math.max(0,Number(values[row][13]||0))+1,nextRetryAfter=new Date(Date.now()+EE_APPLE_ARTIST_DEFERRED_RETRY_MS).toISOString();
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
  var properties=PropertiesService.getScriptProperties(),identity=eeArticleIdentitySheet_().getDataRange().getValues(),artists=eeArtistCatalogueSheet_().getDataRange().getValues(),payloads=eePayloadSheet_().getDataRange().getValues(),result={postsAnalyzed:Math.max(0,identity.length-1),canonicalArtists:Math.max(0,artists.length-1),verifiedAppleIds:0,unresolvedArtists:0,ambiguousArtists:0,deferredArtists:0,artistTransientRetries:0,staleArtists:0,payloadStatus:{READY:0,EMPTY:{},ERROR:{}},appleCalls:Number(properties.getProperty("EE_APPLE_CALL_COUNT")||0),appleCacheHits:Number(properties.getProperty("EE_APPLE_CACHE_HIT_COUNT")||0),catalogueGenerations:Number(properties.getProperty("EE_APPLE_CATALOGUE_GENERATION_COUNT")||0),identityCursor:Number(properties.getProperty("EE_APPLE_IDENTITY_INDEX")||1),artistDiscoveryCursor:Number(properties.getProperty("EE_APPLE_ARTIST_DISCOVERY_INDEX")||1),assemblyCursor:Number(properties.getProperty("EE_APPLE_ASSEMBLY_INDEX")||1),staleRefreshCursor:Number(properties.getProperty("EE_APPLE_STALE_REFRESH_INDEX")||1),cooldownUntil:properties.getProperty("EE_APPLE_COOLDOWN_UNTIL")||null,mostRecentTransientFailure:properties.getProperty("EE_APPLE_LAST_TRANSIENT_FAILURE")||null};
  for(var row=1;row<artists.length;row+=1){if(artists[row][4])result.verifiedAppleIds+=1;if(artists[row][7]==="UNRESOLVED")result.unresolvedArtists+=1;if(artists[row][7]==="AMBIGUOUS")result.ambiguousArtists+=1;if(artists[row][7]==="DEFERRED")result.deferredArtists+=1;result.artistTransientRetries+=Math.max(0,Number(artists[row][13]||0));if(artists[row][10]&&Date.parse(String(artists[row][10]))<=Date.now())result.staleArtists+=1;}
  for(var index=1;index<payloads.length;index+=1){var status=String(payloads[index][5]||""),error=String(payloads[index][6]||"")||"UNCLASSIFIED";if(status==="READY")result.payloadStatus.READY+=1;else if(status==="EMPTY")result.payloadStatus.EMPTY[error]=(result.payloadStatus.EMPTY[error]||0)+1;else if(status==="ERROR")result.payloadStatus.ERROR[error]=(result.payloadStatus.ERROR[error]||0)+1;}
  console.log(JSON.stringify(result));return result;
}


function doGet(event) {
  var params=(event&&event.parameter)||{}, callback=String(params.callback||"");
  var output={schemaVersion:1,postId:String(params.postId||""),categories:[]};

  if (params.action === "payload" && params.postId && eeApplePostAllowed_(params.postId)) {
    output=eePublicPayload_(eeGetPayload_(params.postId))||output;
  }

  var body=JSON.stringify(output);

  if (callback && /^[A-Za-z_$][0-9A-Za-z_$]{0,80}$/.test(callback)) {
    return ContentService.createTextOutput(callback+"("+body+");").setMimeType(ContentService.MimeType.JAVASCRIPT);
  }

  return ContentService.createTextOutput(body).setMimeType(ContentService.MimeType.JSON);
}

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

