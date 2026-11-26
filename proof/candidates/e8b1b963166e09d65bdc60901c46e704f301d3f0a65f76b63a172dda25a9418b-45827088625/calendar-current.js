(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.e8b1b963166e09d6.js","sha256":"e8b1b963166e09d65bdc60901c46e704f301d3f0a65f76b63a172dda25a9418b","count":2115,"publishedAt":"2026-11-26T13:14:05Z","state":"calendar-state.json","stateSha256":"e64715cf0c827d921a55f91c3bd559580aef0e2a71b9eaac6583728eec6a767f","sourceState":"calendar-source-state.json","sourceStateSha256":"4c88bb7598ae7f36ff3ae74f0fca40cd245342ee7f208d2e791e1283d9ca0750"});
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
