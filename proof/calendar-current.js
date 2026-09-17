(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.fa91fa71ce589d4d.js","sha256":"fa91fa71ce589d4dd27104c3a6dd09b4806f8964100f85fb3521303f4aa7a3a8","count":2495,"publishedAt":"2026-09-17T05:01:07Z","state":"calendar-state.json","stateSha256":"8b7032cba0e59d49f584fe28319b8edb595e2113376a28bd846c30de68e3b7ff"});
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
