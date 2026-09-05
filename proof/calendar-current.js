(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.fb08c2201f527d6f.js","sha256":"fb08c2201f527d6ff710e03a0362463898e998699d05a77e62d19c509798beb7","count":2529,"publishedAt":"2026-09-05T04:46:39Z","state":"calendar-state.json","stateSha256":"08b56ecaf999b13e6646b2fd1c2006fc2ac26e283e3995d6d4b08ecaad9e5fa6"});
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
