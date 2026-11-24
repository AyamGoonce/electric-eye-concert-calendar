(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.1a6d0559a0743040.js","sha256":"1a6d0559a074304008ae2f8287710eee2025530790bc76807d9ddf70868fe190","count":2113,"publishedAt":"2026-11-24T17:36:34Z","state":"calendar-state.json","stateSha256":"4527e82e29a16a1e14b206298cbf417b8ce4a3c30d17162cdca5acc33dccfd4c","sourceState":"calendar-source-state.json","sourceStateSha256":"00a42f1f33f67b0c65b8214efc2ae13374c6384a3169f87008aa3c160c6d74fc"});
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
