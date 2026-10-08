(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.a620eb411966b755.js","sha256":"a620eb411966b755f27c558f6b393ce4ee5f11204d232af881bf324f67e834c5","count":2216,"publishedAt":"2026-10-08T18:54:36Z","state":"calendar-state.json","stateSha256":"061efdd125557ce51612e91a8671bf10e1812f945c91b9a3f0fb510b376b7742","sourceState":"calendar-source-state.json","sourceStateSha256":"0b112127ac8953fd66d88a4a60104dc6f074ea76992206dafb1a08f43806f1c7"});
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
