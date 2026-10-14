(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.6f789c7843bcd5bd.js","sha256":"6f789c7843bcd5bd84b744eac1b22c4e9fb26f4c911a006bdc353dece273c768","count":2162,"publishedAt":"2026-10-14T15:47:59Z","state":"calendar-state.json","stateSha256":"8308e02ac0a3cff8047f3cc3eb7223772c25208ff0d6a9d8be670a7921111faa","sourceState":"calendar-source-state.json","sourceStateSha256":"74aa6708c558109d4e9d3a3655239db7efefef095d5143ceab393fffa0e2e21e"});
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
