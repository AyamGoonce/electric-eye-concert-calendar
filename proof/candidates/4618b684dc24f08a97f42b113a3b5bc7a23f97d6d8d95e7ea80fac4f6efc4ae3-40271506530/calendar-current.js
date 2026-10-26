(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.4618b684dc24f08a.js","sha256":"4618b684dc24f08a97f42b113a3b5bc7a23f97d6d8d95e7ea80fac4f6efc4ae3","count":2031,"publishedAt":"2026-10-26T04:57:16Z","state":"calendar-state.json","stateSha256":"148f9aca155e327e03277569040fe3938dcb0fc85cce12a87e0db5a4373146c5","sourceState":"calendar-source-state.json","sourceStateSha256":"b4e11173ae41e31d6ca402d6dc6e787ae028f1f36d5b0619d2e8de37a27f9a0c"});
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
