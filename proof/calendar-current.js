(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.8ca2064e7b5b810b.js","sha256":"8ca2064e7b5b810bdbce0ebf751bfb8ed2e5304b1ee7e5102a6c24a36c2114c9","count":2462,"publishedAt":"2026-09-06T23:05:11Z","state":"calendar-state.json","stateSha256":"e4909806ace8682bd3bdf4a273cca041ecbebc298a9afabf34e6a4e05a3b4cdb"});
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
