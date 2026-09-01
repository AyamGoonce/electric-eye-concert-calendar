(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.c69b1f5a3e401275.js","sha256":"c69b1f5a3e401275232c1e7ecf268f728cd30993842f85b85c7bdcc73f94bb67","count":2265,"publishedAt":"2026-09-01T17:29:23Z","state":"calendar-state.json","stateSha256":"91129603d9a3ea0734d73b4054abe0a903a27d6b3fcbd16847a64cb07ca4ce40"});
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
