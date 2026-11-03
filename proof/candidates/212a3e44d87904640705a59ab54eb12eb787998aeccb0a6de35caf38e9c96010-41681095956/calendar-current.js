(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.212a3e44d8790464.js","sha256":"212a3e44d87904640705a59ab54eb12eb787998aeccb0a6de35caf38e9c96010","count":2050,"publishedAt":"2026-11-03T17:10:30Z","state":"calendar-state.json","stateSha256":"780e4042be4c97ae03769a49c1c2e8f6f66210d425d4a3ff277b87a487cd93e5","sourceState":"calendar-source-state.json","sourceStateSha256":"3842cb34abc5be1fe86ac1a5015bf7c1a4c3b64b8350b01da6afd41d656b3811"});
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
