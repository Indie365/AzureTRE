import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { ApiEndpoint } from '../../models/apiEndpoints';
import { useAuthApiCall, HttpMethod } from '../../useAuthApiCall';
import { ResourceDebug } from '../shared/ResourceDebug';
import { MessageBar, MessageBarType, Pivot, PivotItem, Spinner, SpinnerSize } from '@fluentui/react';
import { ResourcePropertyPanel } from '../shared/ResourcePropertyPanel';
import { LoadingState } from '../../models/loadingState';
import { SharedService } from '../../models/sharedService';

export const SharedServiceItem: React.FunctionComponent = () => {
  const { sharedServiceId } = useParams();
  const [sharedService, setSharedService] = useState({} as SharedService);
  const [loadingState, setLoadingState] = useState(LoadingState.Loading);
  const apiCall = useAuthApiCall();

  useEffect(() => {
    const getData = async () => {
      let ss = await apiCall(`${ApiEndpoint.SharedServices}/${sharedServiceId}`, HttpMethod.Get);
      setSharedService(ss.sharedService);
      setLoadingState(LoadingState.Ok);
    };
    getData();
  }, [apiCall, sharedServiceId]);

  switch (loadingState) {
    case LoadingState.Ok:
      return (
        <>
          <h1>{sharedService.properties?.display_name}</h1>
          <Pivot aria-label="Basic Pivot Example">
            <PivotItem
              headerText="Overview"
              headerButtonProps={{
                'data-order': 1,
                'data-title': 'Overview',
              }}
            >
              <ResourcePropertyPanel resource={sharedService} />
              <ResourceDebug resource={sharedService} />
            </PivotItem>
            <PivotItem headerText="History">
              <h3>--History goes here--</h3>
            </PivotItem>
            <PivotItem headerText="Operations">
              <h3>--Operations Log here</h3>
            </PivotItem>
          </Pivot>
        </>
      );
    case LoadingState.Error:
      return (
        <MessageBar
          messageBarType={MessageBarType.error}
          isMultiline={true}
        >
          <h3>Error retrieving shared service</h3>
          <p>There was an error retrieving this shared service. Please see the browser console for details.</p>
        </MessageBar>
      );
    default:
      return (
        <div style={{ marginTop: '20px' }}>
          <Spinner label="Loading Shared Service" ariaLive="assertive" labelPosition="top" size={SpinnerSize.large} />
        </div>
      )
  }
};
