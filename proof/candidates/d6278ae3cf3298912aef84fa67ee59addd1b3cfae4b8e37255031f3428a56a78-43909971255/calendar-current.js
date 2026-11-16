(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.d6278ae3cf329891.js","sha256":"d6278ae3cf3298912aef84fa67ee59addd1b3cfae4b8e37255031f3428a56a78","count":2111,"publishedAt":"2026-11-16T16:42:51Z","state":"calendar-state.json","stateSha256":"2f12bb7d7d747b2a40dc616160d674a7660441ddbe702a1f73789f4583b16c1f","sourceState":"calendar-source-state.json","sourceStateSha256":"206504cff5ba62fd9ef5641079d36e56864005cf6fa32a4c7ace32e8991844ce"});
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
