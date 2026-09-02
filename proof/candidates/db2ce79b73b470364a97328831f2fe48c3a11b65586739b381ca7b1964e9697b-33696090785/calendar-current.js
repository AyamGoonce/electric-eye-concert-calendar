(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.db2ce79b73b47036.js","sha256":"db2ce79b73b470364a97328831f2fe48c3a11b65586739b381ca7b1964e9697b","count":2209,"publishedAt":"2026-09-02T23:49:22Z","state":"calendar-state.json","stateSha256":"a19e6e5b994cff5e1c82fd40dd19920bd2d4e594ba5af46897fee43a3a0f4912"});
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
