(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.5f240d4b4095ebc0.js","sha256":"5f240d4b4095ebc0264de255b0326560a0f9d0092c1f311831c864a8abbc8b02","count":2192,"publishedAt":"2026-09-19T11:10:51Z","state":"calendar-state.json","stateSha256":"da9060529508818d2cdbb38ceda4e23bfa64f6353b8d5219e2714cb9e0799fc0"});
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
