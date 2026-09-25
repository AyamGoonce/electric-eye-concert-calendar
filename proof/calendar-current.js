(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.c880bd37a622f61c.js","sha256":"c880bd37a622f61cb95c85e562e9ecab50c57b86d059b5ea12ab757cd5d4726d","count":2124,"publishedAt":"2026-09-25T14:27:21Z","state":"calendar-state.json","stateSha256":"d095bc6c4d8b3d36a485fc2b1aa5351a9789d16659cb251035eb7d4314d0a9e3","sourceState":"calendar-source-state.json","sourceStateSha256":"fcdab8d10d036e94766ff5bbf942928dca943cd85ab2f671bad7f73c2f395ce1"});
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
