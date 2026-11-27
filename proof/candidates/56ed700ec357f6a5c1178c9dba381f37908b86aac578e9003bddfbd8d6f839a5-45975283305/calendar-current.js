(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.56ed700ec357f6a5.js","sha256":"56ed700ec357f6a5c1178c9dba381f37908b86aac578e9003bddfbd8d6f839a5","count":2103,"publishedAt":"2026-11-27T09:38:01Z","state":"calendar-state.json","stateSha256":"c6ae352dc01b98c993d62c65b4014f77cd7c16e09d0daf1988c081aaee2fd92c","sourceState":"calendar-source-state.json","sourceStateSha256":"0192867d8681c2e6d24b842fcdc4054db3efba3b1c9435fd97913b105f1d51be"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
