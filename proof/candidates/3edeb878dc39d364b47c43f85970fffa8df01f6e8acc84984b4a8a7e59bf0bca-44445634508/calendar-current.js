(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.3edeb878dc39d364.js","sha256":"3edeb878dc39d364b47c43f85970fffa8df01f6e8acc84984b4a8a7e59bf0bca","count":2113,"publishedAt":"2026-11-19T02:37:28Z","state":"calendar-state.json","stateSha256":"2542be16c41155a46613c5022dc59caf47e0228a81ddc4b83922f390bbcc25c4","sourceState":"calendar-source-state.json","sourceStateSha256":"56b04d5442e1b103218983ad92b5c0d28a7f43a082548220a52dec9ec8ce388c"});
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
