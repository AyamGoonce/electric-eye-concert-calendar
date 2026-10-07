(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.c44cf51966df99ee.js","sha256":"c44cf51966df99eea88a7f9cc4317ee5032b7711997ea67f4adb770318f05939","count":2223,"publishedAt":"2026-10-07T23:01:08Z","state":"calendar-state.json","stateSha256":"c633d207cb5dbe6c07d61903acf2fb8cfa010d73908f5dea0c533eaea74ec826","sourceState":"calendar-source-state.json","sourceStateSha256":"55043a7e8bb46a4b5deb392e9f6abcb22106e6b6bef1e95e9b46d0d0c9fb063f"});
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
