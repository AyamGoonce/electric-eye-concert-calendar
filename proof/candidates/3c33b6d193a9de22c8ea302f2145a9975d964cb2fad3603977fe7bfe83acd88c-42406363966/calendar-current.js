(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.3c33b6d193a9de22.js","sha256":"3c33b6d193a9de22c8ea302f2145a9975d964cb2fad3603977fe7bfe83acd88c","count":2008,"publishedAt":"2026-11-07T19:30:33Z","state":"calendar-state.json","stateSha256":"04765dcac423bfccdd32a2e459c984a7a1c17dfdfa6beee9fa09cc6cf47e397e","sourceState":"calendar-source-state.json","sourceStateSha256":"62c4e35bf4921c2dfedce3a258a515b9da84137772d5c18a373df60268890973"});
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
