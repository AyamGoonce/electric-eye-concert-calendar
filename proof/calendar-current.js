(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.33fdb21a3ff340c1.js","sha256":"33fdb21a3ff340c17cd5ea5ea0bd35d711595a100f2192266c0b31db33a1777e","count":2531,"publishedAt":"2026-09-05T07:10:29Z","state":"calendar-state.json","stateSha256":"7e80f93bc22a9c2f6d6bb0f91f53150ad43cb98413908f68595bc077c65f28bb"});
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
