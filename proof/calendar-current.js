(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.d95d7d9dc01a0fdb.js","sha256":"d95d7d9dc01a0fdb466d842be6b9e2772131417a3457e35905662baa9ae34c95","count":2124,"publishedAt":"2026-09-25T15:28:02Z","state":"calendar-state.json","stateSha256":"ba7be421d3cb279754ef0dbd22a500929f2be126bda3f49ca0c21580e5966ae1","sourceState":"calendar-source-state.json","sourceStateSha256":"52a18d49370cb8b62968f7ef8edcfc7d54e7efae0c5ec716fb9442363d79eb7d"});
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
