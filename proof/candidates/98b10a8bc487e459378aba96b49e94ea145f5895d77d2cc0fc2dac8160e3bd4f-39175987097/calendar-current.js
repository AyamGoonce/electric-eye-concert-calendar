(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.98b10a8bc487e459.js","sha256":"98b10a8bc487e459378aba96b49e94ea145f5895d77d2cc0fc2dac8160e3bd4f","count":2071,"publishedAt":"2026-10-18T23:21:38Z","state":"calendar-state.json","stateSha256":"76d5668a92ed37691b76ea70e90ae5dd1470c8486d57b88d68974188c00b2084","sourceState":"calendar-source-state.json","sourceStateSha256":"db57f03d343c9b164687a481ecd08999ce0118585de615db677d4e128ef802bd"});
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
