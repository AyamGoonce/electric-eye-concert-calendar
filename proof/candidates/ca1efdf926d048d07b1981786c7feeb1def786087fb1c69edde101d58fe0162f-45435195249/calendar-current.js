(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.ca1efdf926d048d0.js","sha256":"ca1efdf926d048d07b1981786c7feeb1def786087fb1c69edde101d58fe0162f","count":2113,"publishedAt":"2026-11-24T16:17:06Z","state":"calendar-state.json","stateSha256":"445cf3107dfa95f45d9b467aafe6e75e31d0dd627b83ec49ba1ab2bfd9e5fe2b","sourceState":"calendar-source-state.json","sourceStateSha256":"34d59a20f0c5a16ebf4bc1d030895195b11b435a1f56826aff8e557c10735546"});
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
