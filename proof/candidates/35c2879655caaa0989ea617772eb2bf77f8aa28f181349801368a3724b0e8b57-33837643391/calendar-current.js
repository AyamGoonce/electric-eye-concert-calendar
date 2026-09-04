(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.35c2879655caaa09.js","sha256":"35c2879655caaa0989ea617772eb2bf77f8aa28f181349801368a3724b0e8b57","count":2527,"publishedAt":"2026-09-04T04:50:50Z","state":"calendar-state.json","stateSha256":"7493096d2a87a0060f9bf037d5b51b24f39b6536f7eb8b392000a9c9816071fb"});
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
