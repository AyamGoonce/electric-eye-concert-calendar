(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.4a975e7fa51049b4.js","sha256":"4a975e7fa51049b4645260cdc240719edce0f5097a8783131a44279c1bf0ea99","count":2069,"publishedAt":"2026-09-27T17:02:07Z","state":"calendar-state.json","stateSha256":"7cf16e047c1f0fbfd9d0c8359f109f4585217d4ad259615c36645a8b22f76eb0","sourceState":"calendar-source-state.json","sourceStateSha256":"a4180785edc232d258ccc7a979355eac875bd763d8bdf0a98a0439fccabcd7f5"});
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
