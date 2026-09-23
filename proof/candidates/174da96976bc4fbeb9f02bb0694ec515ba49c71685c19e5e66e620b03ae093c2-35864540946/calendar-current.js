(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.174da96976bc4fbe.js","sha256":"174da96976bc4fbeb9f02bb0694ec515ba49c71685c19e5e66e620b03ae093c2","count":2142,"publishedAt":"2026-09-23T13:09:44Z","state":"calendar-state.json","stateSha256":"da3a74feb0239dacbb17b73e6c095edd752a4561719216d7ccd69670321f2f8b","sourceState":"calendar-source-state.json","sourceStateSha256":"2d0ec8b18423696d4218223b6ef6a868982ccfb46c81a4cce3db1bdf1971bcb9"});
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
