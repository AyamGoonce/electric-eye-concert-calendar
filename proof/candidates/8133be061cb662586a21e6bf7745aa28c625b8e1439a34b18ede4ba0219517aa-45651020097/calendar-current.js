(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.8133be061cb66258.js","sha256":"8133be061cb662586a21e6bf7745aa28c625b8e1439a34b18ede4ba0219517aa","count":2122,"publishedAt":"2026-11-25T16:06:25Z","state":"calendar-state.json","stateSha256":"15a14b5983d5f2307a95ca1a1480c8d732f4a9481917a99aaf67d4b0e0d25b0b","sourceState":"calendar-source-state.json","sourceStateSha256":"1f720d1d2adb955a5cf78618f3f62741ebb2c8042677e6d58a4ef84f020b4e14"});
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
