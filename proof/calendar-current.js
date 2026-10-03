(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.f4d377e612282330.js","sha256":"f4d377e612282330849560d1f883f25ca7b10a0af2ff8f274c002d835ebd8a2a","count":2201,"publishedAt":"2026-10-03T08:44:36Z","state":"calendar-state.json","stateSha256":"295b21c1ad451fcb0ee644389d85b2c429040f8ec774f4aa0454391a6dd8088b","sourceState":"calendar-source-state.json","sourceStateSha256":"0cbedba132b8089173c5b479109209c070b2bade1278853799ec844e09a2b58e"});
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
